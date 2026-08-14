import React, { useState, useRef } from "react";
import Stepper, { Step } from "../Stepper/Stepper";
import { painAreaService, getApiError } from "../../services/api";
import "./CsvUploadFlow.css";

const TEMPLATE_URL = "/pain_area_template.csv";
const TEMPLATE_FILE_NAME = "AI Intervention Pain Areas Tracker - Master Tracker.csv";

const PHASES = [
  { key: "uploading", label: "Uploading file" },
  { key: "parsing", label: "Parsing & validating CSV" },
  { key: "inserting", label: "Saving records to database" },
  { key: "success", label: "Done" },
];

export default function CsvUploadFlow({ isOpen, onClose, onComplete }) {
  const [step, setStep] = useState(1);
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [phase, setPhase] = useState("idle"); // idle | uploading | parsing | inserting | success | error
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const cancelRef = useRef(false);
  const abortRef = useRef(null);

  if (!isOpen) return null;

  const resetAndClose = () => {
    cancelRef.current = true;
    abortRef.current?.abort();
    setStep(1);
    setFile(null);
    setError("");
    setPhase("idle");
    setProgress({ current: 0, total: 0 });
    onClose();
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await fetch(TEMPLATE_URL);
      if (!response.ok) throw new Error(`Template download failed (${response.status})`);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = TEMPLATE_FILE_NAME;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Failed to download template:", err);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
      setError("");
    }
  };

  const runImport = async () => {
    if (!file) {
      setError("Please select a CSV file first.");
      return;
    }
    setError("");
    cancelRef.current = false;
    abortRef.current = new AbortController();
    setProgress({ current: 0, total: 0 });
    setStep(3);
    setPhase("uploading");

    try {
      const formData = new FormData();
      formData.append("file", file);

      // Backend parses + inserts in a single request; the progress callback
      // drives the phase list (uploading -> inserting) as bytes are sent.
      const response = await painAreaService.uploadCsv(formData, (evt) => {
        if (evt.total) {
          setProgress({ current: evt.loaded, total: evt.total });
          if (evt.progress >= 1) setPhase("inserting");
        }
      }, abortRef.current.signal);

      if (cancelRef.current) return;

      setPhase("success");
      setStep(4);
      onComplete?.(response);
    } catch (err) {
      if (cancelRef.current) return;
      console.error("CSV import failed:", err);
      setError(getApiError(err, "Failed to import CSV. Please check the file and try again."));
      setPhase("error");
    }
  };

  const handleCancel = () => {
    cancelRef.current = true;
    abortRef.current?.abort();
    setPhase("idle");
    setStep(2);
  };

  return (
    <div className="csv-flow-overlay" role="dialog" aria-modal="true">
      <div className="csv-flow-container">
        <button type="button" className="csv-flow-close-btn" onClick={resetAndClose} aria-label="Close">
          <span className="material-symbols-outlined">close</span>
        </button>

        <Stepper
          initialStep={1}
          currentStepOverride={step}
          onStepChange={setStep}
          disableStepIndicators
          nextButtonProps={{ style: { display: "none" } }}
          backButtonProps={{ style: { display: "none" } }}
        >
          {/* Step 1: Download template + Save */}
          <Step>
            <h2>Import Pain Area Records</h2>
            <p className="csv-flow-subtext">
              Download the CSV template, fill it in, then continue to upload.
            </p>
            <p className="csv-flow-subtext">
              If you already have a filled template, you can upload it directly. Just ignore the template download step.
            </p>
            <button type="button" className="csv-flow-secondary-btn" onClick={handleDownloadTemplate}>
              <span className="material-symbols-outlined">download</span>
              Download Template
            </button>

            <ScoringReference />

            <div className="csv-flow-footer">
              <button
                type="button"
                className="csv-flow-primary-btn"
                onClick={() => setStep(2)}
              >
                Save & Continue
              </button>
            </div>
          </Step>

          {/* Step 2: Upload CSV */}
          <Step>
            <h2>Upload Your CSV</h2>
            {error && <div className="csv-flow-error">{error}</div>}
            <label className="csv-flow-dropzone">
              <input type="file" accept=".csv" onChange={handleFileChange} className="csv-flow-dropzone-input" />
              <span className="material-symbols-outlined csv-flow-dropzone-icon">upload_file</span>
              <p className="csv-flow-dropzone-text">
                {file ? file.name : "Click to browse or drag & drop your CSV file"}
              </p>
              <p className="csv-flow-dropzone-hint">Supports .csv files only</p>
            </label>
            <div className="csv-flow-footer csv-flow-footer-spread">
              <button type="button" className="csv-flow-back-btn" onClick={() => setStep(1)}>
                Back
              </button>
              <button
                type="button"
                className="csv-flow-primary-btn"
                disabled={!file}
                onClick={runImport}
              >
                Next
              </button>
            </div>
          </Step>

          {/* Step 3: Processing animation */}
          <Step>
            <ProcessingView
              phase={phase}
              progress={progress}
              error={error}
              onCancel={handleCancel}
              onRetry={runImport}
            />
          </Step>

          {/* Step 4: Done */}
          <Step>
            <div className="csv-flow-done">
              <span className="material-symbols-outlined csv-flow-done-icon">check_circle</span>
              <h2>Import Complete</h2>
              <div className="csv-flow-footer">
                <button type="button" className="csv-flow-primary-btn" onClick={resetAndClose}>
                  Done
                </button>
              </div>
            </div>
          </Step>
        </Stepper>
      </div>
    </div>
  );
}

function ScoringReference() {
  const scoreRows = [
    {
      field: "Impact Score",
      source: "Time Spent / Month (Hrs)",
      rules: [
        { condition: "≥ 40 hrs", score: 3 },
        { condition: "≥ 10 hrs", score: 2 },
        { condition: "< 10 hrs or blank", score: 1 },
      ],
    },
    {
      field: "Feasibility Score",
      source: "Feasibility",
      rules: [
        { condition: "High", score: 3 },
        { condition: "Medium", score: 2 },
        { condition: "Low", score: 1 },
      ],
    },
    {
      field: "Priority Score",
      source: "Priority",
      rules: [
        { condition: "High", score: 3 },
        { condition: "Medium", score: 2 },
        { condition: "Low", score: 1 },
      ],
    },
  ];

  const quadrants = [
    { name: "Quick Win", impact: "≥ 2", feasibility: "≥ 2", color: "#16A34A" },
    { name: "Strategic", impact: "≥ 2", feasibility: "< 2", color: "#2563EB" },
    { name: "Fill In", impact: "< 2", feasibility: "≥ 2", color: "#D97706" },
    { name: "Revisit", impact: "< 2", feasibility: "< 2", color: "#94A3B8" },
  ];

  return (
    <div className="csv-flow-reference">
      <h3>How scores are calculated</h3>
      <p className="csv-flow-reference-sub">
        These read-only fields are derived automatically after import — you only fill in the source columns.
      </p>
      <div className="csv-flow-reference-grid">
        {scoreRows.map((row) => (
          <div key={row.field} className="csv-flow-reference-card">
            <p className="csv-flow-reference-field">{row.field}</p>
            <p className="csv-flow-reference-source">from {row.source}</p>
            <ul className="csv-flow-reference-rules">
              {row.rules.map((rule) => (
                <li key={rule.condition} className="csv-flow-reference-rule">
                  <span className="csv-flow-reference-score">{rule.score}</span>
                  <span>{rule.condition}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
        <div className="csv-flow-reference-card">
          <p className="csv-flow-reference-field">Quadrant</p>
          <p className="csv-flow-reference-source">from Impact × Feasibility</p>
          <ul className="csv-flow-reference-rules">
            {quadrants.map((q) => (
              <li key={q.name} className="csv-flow-reference-rule">
                <span className="csv-flow-reference-dot" style={{ background: q.color }} />
                <span>
                  {q.name} · impact {q.impact} &amp; feasibility {q.feasibility}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

function ProcessingView({ phase, progress, error, onCancel, onRetry }) {
  const activeIndex = PHASES.findIndex((p) => p.key === phase);

  return (
    <div className="csv-flow-processing" aria-live="polite">
      <h2>Processing Your File</h2>

      <ul className="csv-flow-phase-list">
        {PHASES.map((p, i) => {
          const status =
            phase === "error" && i === activeIndex
              ? "error"
              : i < activeIndex || phase === "success"
              ? "complete"
              : i === activeIndex
              ? "active"
              : "pending";

          return (
            <li key={p.key} className={`csv-flow-phase csv-flow-phase-${status}`}>
              <span className="csv-flow-phase-dot" />
              <span>{p.label}</span>
              {status === "active" && p.key === "inserting" && progress.total > 0 && (
                <span className="csv-flow-phase-count">
                  {progress.current} / {progress.total}
                </span>
              )}
            </li>
          );
        })}
      </ul>

      {phase === "error" ? (
        <>
          <div className="csv-flow-error">{error}</div>
          <div className="csv-flow-footer">
            <button type="button" className="csv-flow-back-btn" onClick={onCancel}>
              Back
            </button>
            <button type="button" className="csv-flow-primary-btn" onClick={onRetry}>
              Retry
            </button>
          </div>
        </>
      ) : (
        <div className="csv-flow-footer csv-flow-footer-end">
          <button type="button" className="csv-flow-cancel-link" onClick={onCancel}>
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}

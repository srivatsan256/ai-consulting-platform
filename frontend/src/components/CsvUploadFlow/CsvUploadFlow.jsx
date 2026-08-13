import React, { useState, useRef } from "react";
import Stepper, { Step } from "../Stepper/Stepper";
import { painAreaService, getApiError } from "../../services/api";
import "./CsvUploadFlow.css";

const TEMPLATE_HEADERS = [
  "date",
  "department",
  "process_activity",
  "pain_area",
  "current_method",
  "frequency",
  "time_spent_hrs",
  "impact_area",
  "ai_intervention",
  "expected_benefit",
  "priority",
  "feasibility",
  "owner",
  "target_date",
  "status",
  "remarks",
];

const TEMPLATE_SAMPLE_ROW = [
  "2026-08-13",
  "Operations",
  "Invoice Processing",
  "Manual data entry takes 3+ hours per day",
  "Manual entry into spreadsheets",
  "Daily",
  "60",
  "Speed, Cost",
  "Automated invoice data extraction",
  "Save ~50 hours per month",
  "High",
  "High",
  "Jane Doe",
  "2026-10-01",
  "Open",
  "Prioritize before month-end close",
];

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
  const [summary, setSummary] = useState(null);
  const cancelRef = useRef(false);

  if (!isOpen) return null;

  const resetAndClose = () => {
    cancelRef.current = true;
    setStep(1);
    setFile(null);
    setError("");
    setPhase("idle");
    setProgress({ current: 0, total: 0 });
    setSummary(null);
    onClose();
  };

  const handleDownloadTemplate = () => {
    const csvContent = [
      TEMPLATE_HEADERS.join(","),
      TEMPLATE_SAMPLE_ROW.join(","),
    ].join("\n");
    const blob = new Blob(["\ufeff", csvContent], {
      type: "text/csv;charset=utf-8;",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "pain_area_template.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
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
    setStep(3);
    setPhase("uploading");

    try {
      const formData = new FormData();
      formData.append("file", file);

      setPhase("parsing");
      // Backend does the real parse/insert; we call once and reflect
      // stage-by-stage UI while awaiting the response.
      setPhase("inserting");

      const response = painAreaService.uploadCsv
        ? await painAreaService.uploadCsv(formData, (evt) => {
            if (evt.total) {
              setProgress({ current: evt.loaded, total: evt.total });
            }
          })
        : await painAreaService.create(formData);

      if (cancelRef.current) return;

      setSummary({
        inserted: response?.data?.inserted ?? response?.inserted ?? 0,
        skipped: response?.data?.skipped ?? response?.skipped ?? 0,
        warnings: response?.data?.warnings ?? response?.warnings ?? [],
      });
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
            <button type="button" className="csv-flow-secondary-btn" onClick={handleDownloadTemplate}>
              <span className="material-symbols-outlined">download</span>
              Download Template
            </button>
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
              {summary && (
                <p className="csv-flow-subtext">
                  {summary.inserted} record{summary.inserted === 1 ? "" : "s"} imported
                  {summary.skipped ? `, ${summary.skipped} skipped` : ""}.
                </p>
              )}
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

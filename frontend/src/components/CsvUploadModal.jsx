import React, { useState, useEffect } from "react";
import { painAreaService, getApiError } from "../services/api";
import "../styles/components/CsvUploadModal.css";

const TEMPLATE_SAVED_KEY = "pain_area_template_saved";

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

const STEP_LABELS = ["Template", "Upload", "Processing"];

export default function CsvUploadModal({ isOpen, onClose, onUploadSuccess }) {
  const [step, setStep] = useState(1);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [closing, setClosing] = useState(false);
  const [templateDownloaded, setTemplateDownloaded] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setClosing(false);
      setFile(null);
      setError("");
      const saved = localStorage.getItem(TEMPLATE_SAVED_KEY) === "true";
      setTemplateDownloaded(saved);
      setStep(saved ? 2 : 1);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleClose = () => {
    if (closing) return;
    setClosing(true);
    setTimeout(() => {
      setClosing(false);
      onClose();
    }, 200);
  };

  const downloadTemplate = () => {
    const csvContent = [
      TEMPLATE_HEADERS.join(","),
      TEMPLATE_SAMPLE_ROW.join(","),
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "pain_area_template.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    setTemplateDownloaded(true);
    setError("");
  };

  const handleSaveTemplate = () => {
    localStorage.setItem(TEMPLATE_SAVED_KEY, "true");
    handleClose();
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError("");
    }
  };

  const handleNext = () => {
    if (!file) {
      setError("Please select a CSV file first.");
      return;
    }
    setError("");
    setStep(3);
    handleUpload();
  };

  const handleUpload = async () => {
    setUploading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      if (painAreaService.uploadCsv) {
        await painAreaService.uploadCsv(formData);
      } else {
        await painAreaService.create(formData);
      }

      setUploading(false);
      onUploadSuccess();
      handleClose();
    } catch (err) {
      console.error("CSV upload failed:", err);
      setError(
        getApiError(
          err,
          "Failed to upload CSV file. Please check the file format."
        )
      );
      setUploading(false);
      setStep(2);
    }
  };

  const getStepStatus = (index) => {
    if (step > index) return "complete";
    if (step === index) return "active";
    return "inactive";
  };

  return (
    <div
      className={`csv-modal-overlay ${closing ? "csv-modal-closing" : ""}`}
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) handleClose();
      }}
    >
      <div className={`csv-modal-container ${closing ? "csv-modal-closing" : ""}`}>
        <div className="csv-modal-header">
          <h3 className="csv-modal-title">Upload Pain Areas via CSV</h3>

          <button
            type="button"
            onClick={handleClose}
            className="csv-modal-close-btn"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <div className="csv-stepper">
          {STEP_LABELS.map((label, index) => {
            const stepNumber = index + 1;
            const status = getStepStatus(stepNumber);
            return (
              <React.Fragment key={label}>
                {index > 0 && (
                  <div
                    className={`csv-stepper-line ${
                      stepNumber <= step ? "complete" : ""
                    }`}
                  />
                )}
                <div className={`csv-stepper-step ${status}`}>
                  <span className="csv-stepper-circle">
                    {status === "complete" ? (
                      <span className="material-symbols-outlined csv-stepper-check">
                        check
                      </span>
                    ) : (
                      stepNumber
                    )}
                  </span>
                  <span className="csv-stepper-label">{label}</span>
                </div>
              </React.Fragment>
            );
          })}
        </div>

        {error && <div className="csv-modal-error">{error}</div>}

        {step === 1 && (
          <div key="step-1" className="csv-step-content csv-step-enter">
            <p className="csv-step-text">
              Download the CSV template, fill it with your pain area records,
              then save to continue.
            </p>

            <button
              type="button"
              onClick={downloadTemplate}
              className="csv-download-btn"
            >
              <span className="material-symbols-outlined">download</span>
              Download Template
            </button>

            {templateDownloaded && (
              <p className="csv-step-hint">
                Template downloaded. Fill it in and save to continue.
              </p>
            )}

            <div className="csv-modal-footer">
              <button
                type="button"
                onClick={handleClose}
                className="csv-cancel-btn"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={handleSaveTemplate}
                disabled={!templateDownloaded}
                className="csv-submit-btn"
              >
                Save
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div key="step-2" className="csv-step-content csv-step-enter">
            <div className="csv-dropzone">
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="csv-dropzone-input"
              />

              <span className="material-symbols-outlined csv-dropzone-icon">
                upload_file
              </span>

              <p className="csv-dropzone-text">
                {file
                  ? file.name
                  : "Click to browse or drag & drop your CSV file"}
              </p>

              <p className="csv-dropzone-hint">Supports .csv files only</p>
            </div>

            <div className="csv-modal-footer">
              <button
                type="button"
                onClick={handleClose}
                className="csv-cancel-btn"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={handleNext}
                disabled={!file}
                className="csv-submit-btn"
              >
                Next
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div key="step-3" className="csv-step-content csv-step-enter">
            <div className="csv-processing">
              <div className="csv-spinner" />
              <p className="csv-processing-text">
                {uploading
                  ? "Processing your CSV file..."
                  : "Completed"}
              </p>
              <p className="csv-processing-hint">
                Please wait while your records are uploaded.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

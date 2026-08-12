import React, { useState, useEffect } from "react";
import { projectService, verificationService } from "../services/api";
import TopHeader from "../components/TopHeader";
import "../styles/pages/VerificationPage.css";

export default function VerificationPage({ projectId, onSelectProject }) {
  const [projects, setProjects] = useState([]);
  const [selectedId, setSelectedId] = useState(projectId || "");
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [useAi, setUseAi] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => { fetchProjects(); }, []);
  useEffect(() => {
    if (projectId) {
      setSelectedId(projectId);
      fetchProjectDetail(projectId);
    }
  }, [projectId]);

  const fetchProjects = async () => {
    try {
      const res = await projectService.list();
      setProjects(res.data.results || res.data || []);
    } catch (err) {
      console.error("Failed to fetch projects:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchProjectDetail = async (id) => {
    try {
      const res = await projectService.get(id);
      setProject(res.data);
      if (res.data.verification_report) {
        setResult({
          readiness_score: res.data.readiness_score,
          status: res.data.status,
          results:
            res.data.verification_report.results ||
            res.data.verification_report.report_data?.documents ||
            [],
        });
      }
    } catch (err) {
      console.error("Failed to fetch project:", err);
    }
  };

  const handleVerify = async () => {
    if (!selectedId) return;
    setVerifying(true);
    setResult(null);
    try {
      const res = await verificationService.verifyAll(selectedId, useAi);
      setResult(res.data);
      fetchProjectDetail(selectedId);
    } catch (err) {
      console.error("Verification failed:", err);
    } finally {
      setVerifying(false);
    }
  };

  const handleProjectSelect = (id) => {
    setSelectedId(id);
    setResult(null);
    setProject(null);
    if (id) fetchProjectDetail(id);
  };

  return (
    <div className="space-y-6">
      <TopHeader
        title="Document Verification"
        subtitle="Verify document completeness"
      />

      {/* Project Selector + Controls */}
      <div className="verify-card soft-shadow">
        <div className="verify-controls">
          <select
            value={selectedId}
            onChange={(e) => handleProjectSelect(e.target.value)}
            className="verify-select"
          >
            <option value="">Select a project</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>{p.project_name} ({p.company_name})</option>
            ))}
          </select>
          <label className="verify-ai-label">
            <input
              type="checkbox"
              checked={useAi}
              onChange={(e) => setUseAi(e.target.checked)}
              className="verify-ai-checkbox"
            />
            AI Analysis
          </label>
          <button
            onClick={handleVerify}
            disabled={!selectedId || verifying || !project?.documents?.length}
            className="verify-btn"
          >
            {verifying ? (
              <div className="w-4 h-4 border-2 border-on-primary border-t-transparent rounded-full animate-spin" />
            ) : (
              <span className="material-symbols-outlined text-[18px]">verified_user</span>
            )}
            {verifying ? "Verifying..." : "Run Verification"}
          </button>
        </div>
      </div>

      {/* No project selected */}
      {!selectedId && !loading && (
        <div className="verify-empty">
          <span className="material-symbols-outlined verify-empty-icon">verified_user</span>
          <p className="verify-empty-text">Select a project to run document verification</p>
        </div>
      )}

      {/* Project with no documents */}
      {selectedId && project && (!project.documents || project.documents.length === 0) && (
        <div className="verify-empty">
          <span className="material-symbols-outlined verify-empty-icon">upload_file</span>
          <p className="verify-empty-text">No documents uploaded for this project</p>
          <button
            onClick={() => onSelectProject(selectedId)}
            className="verify-empty-btn"
          >
            Upload Documents
          </button>
        </div>
      )}

      {/* Verification Results */}
      {result && (
        <div className="space-y-4">
          {/* Readiness Score Card */}
          <div className="verify-score-card soft-shadow">
            <div className="verify-score-inner">
              <div className={`verify-score-circle ${
                result.readiness_score >= 90 ? "bg-emerald-100" : result.readiness_score >= 70 ? "bg-amber-100" : "bg-red-100"
              }`}>
                <span className={`verify-score-value ${
                  result.readiness_score >= 90 ? "text-emerald-700" : result.readiness_score >= 70 ? "text-amber-700" : "text-red-700"
                }`}>
                  {result.readiness_score}%
                </span>
              </div>
              <div>
                <h3 className="verify-score-title">Readiness Score</h3>
                <p className="verify-score-desc">
                  {result.readiness_score >= 90
                    ? "Documents meet readiness threshold. Ready for next phase."
                    : "Documents need improvement. Review missing items below."}
                </p>
              </div>
              <div className={`verify-status-pill ${
                result.readiness_score >= 90
                  ? "bg-emerald-100 text-emerald-700"
                  : "bg-amber-100 text-amber-700"
              }`}>
                {result.readiness_score >= 90 ? "Ready" : "Needs Work"}
              </div>
            </div>
            {/* Progress bar */}
            <div className="verify-progress-track">
              <div
                className={`verify-progress-fill ${
                  result.readiness_score >= 90 ? "bg-emerald-500" : result.readiness_score >= 70 ? "bg-amber-500" : "bg-red-500"
                }`}
                style={{ width: `${result.readiness_score}%` }}
              />
            </div>
          </div>

          {/* Document Results */}
          {result.results?.map((docResult, idx) => (
            <div key={idx} className="verify-doc-card soft-shadow">
              <div className="verify-doc-header">
                <span className={`verify-doc-dot ${docResult.passed ? "bg-emerald-500" : "bg-red-500"}`} />
                <h4 className="verify-doc-title">{docResult.doc_type} Document</h4>
                <span className={`verify-doc-score ${
                  docResult.passed ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"
                }`}>
                  {docResult.score}%
                </span>
              </div>

              {/* Score bar */}
              <div className="verify-doc-track">
                <div
                  className={`verify-doc-fill ${docResult.passed ? "bg-emerald-500" : "bg-red-500"}`}
                  style={{ width: `${docResult.score}%` }}
                />
              </div>

              {/* Missing Keywords */}
              {docResult.missing_keywords?.length > 0 && (
                <div className="mb-3">
                  <p className="verify-missing-label">Missing Keywords</p>
                  <div className="verify-chip-wrap">
                    {docResult.missing_keywords.map((kw, i) => (
                      <span key={i} className="verify-chip-red">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Missing Sections */}
              {docResult.missing_sections?.length > 0 && (
                <div className="mb-3">
                  <p className="verify-missing-label-amber">Missing Sections</p>
                  <div className="verify-chip-wrap">
                    {docResult.missing_sections.map((sec, i) => (
                      <span key={i} className="verify-chip-amber">
                        {sec}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* AI Feedback */}
              {docResult.ai_feedback && (
                <div className="verify-ai">
                  <p className="verify-ai-label">AI Analysis</p>
                  <p className="verify-ai-text">{docResult.ai_feedback}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {selectedId && project && project.documents?.length > 0 && !result && !verifying && (
        <div className="verify-hint">
          <span className="material-symbols-outlined verify-hint-icon">rate_review</span>
          <p className="verify-hint-text">Click "Run Verification" to analyze {project.documents.length} document(s)</p>
        </div>
      )}
    </div>
  );
}

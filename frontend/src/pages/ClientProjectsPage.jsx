import React, { useState, useEffect } from "react";
import { projectService } from "../services/api";
import TopHeader from "../components/TopHeader";
import "./ClientProjectsPage.css";

const STATUS_COLORS = {
  DISCOVERY: "bg-blue-100 text-blue-700",
  VERIFICATION: "bg-amber-100 text-amber-700",
  PROCESSING: "bg-purple-100 text-purple-700",
  REVIEW: "bg-indigo-100 text-indigo-700",
  COMPLETED: "bg-emerald-100 text-emerald-700",
  ON_HOLD: "bg-gray-100 text-gray-600",
};

export default function ClientProjectsPage({ projectId, onSelectProject, onBack }) {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState(projectId || "");
  const [project, setProject] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => { fetchProjects(); }, []);
  useEffect(() => {
    if (projectId) {
      setSelectedId(projectId);
      fetchProject(projectId);
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

  const fetchProject = async (id) => {
    setDetailLoading(true);
    try {
      const res = await projectService.get(id);
      setProject(res.data);
    } catch (err) {
      console.error("Failed to fetch project:", err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleProjectSelect = (id) => {
    setSelectedId(id);
    setProject(null);
    if (id) fetchProject(id);
  };

  const openDocument = (fileUrl) => {
    if (fileUrl) window.open(fileUrl, "_blank", "noopener,noreferrer");
  };

  const report = project?.verification_report;
  const reportResults = report?.results || report?.report_data?.documents || [];

  return (
    <div className="space-y-6">
      <TopHeader title="My Projects" subtitle="View your consulting engagements" />

      {/* Project Selector */}
      <div className="clientprojects-selector-card">
        <label className="clientprojects-label">
          Select Project
        </label>
        <select
          value={selectedId}
          onChange={(e) => handleProjectSelect(e.target.value)}
          className="clientprojects-select"
        >
          <option value="">Choose a project</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>
              {p.project_name} ({p.company_name})
            </option>
          ))}
        </select>
      </div>

      {!selectedId && !loading && (
        <div className="clientprojects-empty">
          <span className="material-symbols-outlined clientprojects-empty-icon">folder_open</span>
          <p className="clientprojects-empty-text">Select a project to view its details</p>
        </div>
      )}

      {selectedId && detailLoading && (
        <div className="clientprojects-spinner-wrap">
          <div className="clientprojects-spinner" />
        </div>
      )}

      {selectedId && project && (
        <div className="space-y-6">
          <div className="clientprojects-card">
            <div className="clientprojects-detail-head">
              <div className="clientprojects-icon-box">
                <span className="material-symbols-outlined clientprojects-icon">folder</span>
              </div>
              <div className="clientprojects-title-wrap">
                <h3 className="clientprojects-title">{project.project_name}</h3>
                <p className="clientprojects-subtitle">
                  {project.company_name} · {project.industry || "General"}
                </p>
              </div>
              <div className="clientprojects-badges">
                {project.readiness_score != null && (
                  <span className={`clientprojects-badge ${
                    project.readiness_score >= 90 ? "bg-emerald-100 text-emerald-700" : project.readiness_score >= 70 ? "bg-amber-100 text-amber-700" : "bg-red-100 text-red-700"
                  }`}>
                    {project.readiness_score}% ready
                  </span>
                )}
                <span className={`clientprojects-badge ${STATUS_COLORS[project.status] || "bg-gray-100 text-gray-600"}`}>
                  {project.status}
                </span>
              </div>
            </div>
            <div className="clientprojects-progress-track">
              <div className="clientprojects-progress-fill" style={{ width: `${project.readiness_score || 0}%` }} />
            </div>
            <div className="clientprojects-stats">
              <div>
                <p className="clientprojects-stat-label">Current Level</p>
                <p className="clientprojects-stat-value">L{Math.max(1, project.current_level || 1)}</p>
              </div>
              <div>
                <p className="clientprojects-stat-label">Documents</p>
                <p className="clientprojects-stat-value">{project.documents?.length || 0}</p>
              </div>
              <div>
                <p className="clientprojects-stat-label">Expected Timeline</p>
                <p className="clientprojects-stat-value">{project.expected_timeline || "N/A"}</p>
              </div>
            </div>
          </div>

          {/* Objectives */}
          {project.objectives && (
            <div className="clientprojects-card">
              <h4 className="clientprojects-label">Objectives</h4>
              <p className="text-sm text-on-surface leading-relaxed">{project.objectives}</p>
            </div>
          )}

          {/* Documents */}
          <div className="clientprojects-card">
            <div className="clientprojects-section-head">
              <h3 className="clientprojects-section-title">Documents</h3>
              <span className="clientprojects-section-meta">{project.documents?.length || 0} uploaded</span>
            </div>
            {project.documents?.length ? (
              <div className="clientprojects-doc-list">
                {project.documents.map((doc) => (
                  <div key={doc.id} className="clientprojects-doc-row">
                    <span className="material-symbols-outlined clientprojects-doc-icon">description</span>
                    <div className="clientprojects-doc-info">
                      <p className="clientprojects-doc-name">{doc.original_name}</p>
                      <p className="clientprojects-doc-meta">
                        {doc.doc_type} · Level {doc.level} · Uploaded {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : "N/A"}
                      </p>
                    </div>
                    <span className={`clientprojects-doc-badge ${
                      doc.verification_status ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"
                    }`}>
                      {doc.verification_status ? "Passed" : "Pending"}
                    </span>
                    <button
                      onClick={() => openDocument(doc.file_url)}
                      disabled={!doc.file_url}
                      className="clientprojects-doc-btn"
                    >
                      <span className="material-symbols-outlined clientprojects-doc-btn-icon">open_in_new</span>
                      View
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="clientprojects-no-docs">No documents uploaded yet</p>
            )}
          </div>

          {/* Verification Report */}
          {reportResults.length > 0 && (
            <div className="clientprojects-card">
              <h3 className="clientprojects-report-title">Verification Report</h3>
              <div className="clientprojects-report-list">
                {reportResults.map((result, idx) => (
                  <div key={idx} className="clientprojects-report-item">
                    <div className="clientprojects-report-head">
                      <span className={`clientprojects-report-dot ${result.passed ? "bg-emerald-500" : "bg-red-500"}`} />
                      <span className="clientprojects-report-type">{result.doc_type} Document</span>
                      <span className={`clientprojects-report-score ${
                        result.passed ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"
                      }`}>
                        {result.score}%
                      </span>
                    </div>
                    {result.evidence && (
                      <p className="clientprojects-report-evidence">{result.evidence}</p>
                    )}
                    {result.ai_feedback && (
                      <p className="clientprojects-report-feedback">{result.ai_feedback}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

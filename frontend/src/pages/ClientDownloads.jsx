import React, { useState, useEffect } from "react";
import { projectService, deliverableService } from "../services/api";
import TopHeader from "../components/TopHeader";
import "../styles/pages/ClientDownloads.css";

export default function ClientDownloads({ projectId }) {
  const [projects, setProjects] = useState([]);
  const [selectedId, setSelectedId] = useState(projectId || "");
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [zipUrl, setZipUrl] = useState(null);

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
    try {
      const res = await projectService.get(id);
      setProject(res.data);
    } catch (err) {
      console.error("Failed to fetch project:", err);
    }
  };

  const handleProjectSelect = (id) => {
    setSelectedId(id);
    setProject(null);
    setZipUrl(null);
    if (id) fetchProject(id);
  };

  const handleGenerate = async () => {
    if (!selectedId) return;
    setGenerating(true);
    setZipUrl(null);
    try {
      const res = await deliverableService.generate(selectedId);
      setZipUrl(res.data.zip_download_url);
      fetchProject(selectedId);
    } catch (err) {
      console.error("Generation failed:", err);
    } finally {
      setGenerating(false);
    }
  };

  const downloadUrl = (url) => {
    if (url) window.open(url, "_blank", "noopener,noreferrer");
  };

  return (
    <div className="space-y-6">
      <TopHeader title="Downloads" subtitle="Documents and deliverables" />

      {/* Project Selector */}
      <div className="clientdl-card soft-shadow">
        <label className="clientdl-label">
          Select Project
        </label>
        <select
          value={selectedId}
          onChange={(e) => handleProjectSelect(e.target.value)}
          className="clientdl-select"
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
        <div className="clientdl-empty">
          <span className="material-symbols-outlined clientdl-empty-icon">download</span>
          <p className="clientdl-empty-text">Select a project to download documents and deliverables</p>
        </div>
      )}

      {selectedId && project && (
        <div className="space-y-6">
          {/* Documents */}
          <div className="clientdl-card soft-shadow">
            <div className="clientdl-section-head">
              <h3 className="clientdl-section-title">Project Documents</h3>
              <span className="clientdl-section-meta">{project.documents?.length || 0} uploaded</span>
            </div>
            {project.documents?.length ? (
              <div className="clientdl-doc-list">
                {project.documents.map((doc) => (
                  <div key={doc.id} className="clientdl-doc-row">
                    <span className="material-symbols-outlined clientdl-doc-icon">description</span>
                    <div className="clientdl-doc-info">
                      <p className="clientdl-doc-name">{doc.original_name}</p>
                      <p className="clientdl-doc-meta">
                        {doc.doc_type} · Level {doc.level} ·{" "}
                        {doc.verification_status ? "Verified" : "Pending verification"}
                      </p>
                    </div>
                    <button
                      onClick={() => downloadUrl(doc.file_url)}
                      disabled={!doc.file_url}
                      className="clientdl-doc-btn"
                    >
                      <span className="material-symbols-outlined clientdl-doc-btn-icon">download</span>
                      Download
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="clientdl-no-docs">No documents uploaded yet</p>
            )}
          </div>

          {/* Deliverables */}
          <div className="clientdl-deliverables-card soft-shadow">
            <span className="material-symbols-outlined clientdl-deliverables-icon">assignment_turned_in</span>
            <h4 className="clientdl-deliverables-title">Project Deliverables</h4>
            <p className="clientdl-deliverables-desc">
              BRD, FRD, PRD, verification summary, project timeline and metadata packaged as a ZIP.
            </p>
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="clientdl-generate-btn"
            >
              {generating ? (
                <div className="clientdl-generate-spinner" />
              ) : (
                <span className="material-symbols-outlined clientdl-generate-icon">auto_awesome</span>
              )}
              {generating ? "Generating Deliverables..." : "Generate Deliverables ZIP"}
            </button>

            {zipUrl && (
              <div className="clientdl-ready-card">
                <span className="material-symbols-outlined clientdl-ready-icon" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                <div className="clientdl-ready-info">
                  <p className="clientdl-ready-title">Deliverables ready</p>
                  <p className="clientdl-ready-sub">Your ZIP package is available to download</p>
                </div>
                <a
                  href={zipUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="clientdl-zip-btn"
                >
                  <span className="material-symbols-outlined clientdl-zip-btn-icon">download</span>
                  Download ZIP
                </a>
              </div>
            )}
          </div>

          {/* Verification Summary */}
          {project.verification_report && (
            <div className="clientdl-card soft-shadow">
              <h3 className="clientdl-summary-title">Verification Summary</h3>
              <div className="clientdl-summary-grid">
                <div className="clientdl-summary-item">
                  <p className="clientdl-summary-label">Readiness Score</p>
                  <p className="clientdl-summary-value">{project.readiness_score}%</p>
                </div>
                <div className="clientdl-summary-item">
                  <p className="clientdl-summary-label">Current Level</p>
                  <p className="clientdl-summary-value">L{Math.max(1, project.current_level || 1)}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

import React, { useState, useEffect } from "react";
import { projectService, deliverableService } from "../services/api";
import TopHeader from "../components/TopHeader";
import "../styles/pages/DeliverablesPage.css";

export default function DeliverablesPage({ projectId, onSelectProject }) {
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

  const handleProjectSelect = (id) => {
    setSelectedId(id);
    setProject(null);
    setZipUrl(null);
    if (id) fetchProject(id);
  };

  const deliverableTypes = [
    { icon: "description", title: "BRD", desc: "Business Requirements Document", color: "bg-blue-50 text-blue-600" },
    { icon: "article", title: "FRD", desc: "Functional Requirements Document", color: "bg-purple-50 text-purple-600" },
    { icon: "newspaper", title: "PRD", desc: "Product Requirements Document", color: "bg-emerald-50 text-emerald-600" },
    { icon: "summarize", title: "Verification Summary", desc: "Document verification results", color: "bg-amber-50 text-amber-600" },
    { icon: "timeline", title: "Project Timeline", desc: "Project schedule and milestones", color: "bg-indigo-50 text-indigo-600" },
    { icon: "info", title: "Project Metadata", desc: "Project configuration details", color: "bg-pink-50 text-pink-600" },
  ];

  return (
    <div className="space-y-6">
      <TopHeader title="Deliverables" subtitle="Generate consulting documents" />

      {/* Project Selector */}
      <div className="deliverables-card soft-shadow">
        <select
          value={selectedId}
          onChange={(e) => handleProjectSelect(e.target.value)}
          className="deliverables-select"
        >
          <option value="">Select a project</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.project_name} ({p.company_name})</option>
          ))}
        </select>
      </div>

      {selectedId && (
        <>
          {/* Deliverable Types */}
          <div className="deliverables-grid">
            {deliverableTypes.map((item) => (
              <div key={item.title} className="deliverables-type-card soft-shadow">
                <div className={`deliverables-icon ${item.color}`}>
                  <span className="material-symbols-outlined">{item.icon}</span>
                </div>
                <h4 className="deliverables-type-title">{item.title}</h4>
                <p className="deliverables-type-desc">{item.desc}</p>
              </div>
            ))}
          </div>

          {/* Generate Button */}
          <div className="deliverables-gen-card soft-shadow">
            <span className="material-symbols-outlined deliverables-gen-icon">auto_awesome</span>
            <h4 className="deliverables-gen-title">Generate All Deliverables</h4>
            <p className="deliverables-gen-desc">
              AI will generate BRD, FRD, PRD, verification summary, project timeline, and metadata as a downloadable ZIP.
            </p>
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="deliverables-gen-btn"
            >
              {generating ? (
                <div className="w-4 h-4 border-2 border-on-primary border-t-transparent rounded-full animate-spin" />
              ) : (
                <span className="material-symbols-outlined text-[18px]">auto_awesome</span>
              )}
              {generating ? "Generating Deliverables..." : "Generate ZIP Package"}
            </button>
          </div>

          {/* Download Available */}
          {zipUrl && (
            <div className="deliverables-download-card">
              <span className="material-symbols-outlined deliverables-download-icon" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
              <div className="flex-1">
                <p className="deliverables-download-title">Deliverables Generated Successfully</p>
                <p className="deliverables-download-sub">All documents have been packaged into a ZIP file</p>
              </div>
              <a
                href={zipUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="deliverables-download-link"
              >
                <span className="material-symbols-outlined text-[18px]">download</span>
                Download ZIP
              </a>
            </div>
          )}

          {/* Project Status */}
          {project?.status === "COMPLETED" && (
            <div className="deliverables-status-card">
              <span className="material-symbols-outlined deliverables-status-icon" style={{ fontVariationSettings: "'FILL' 1" }}>info</span>
              <div>
                <p className="deliverables-status-title">Project Completed</p>
                <p className="deliverables-status-sub">All deliverables have been generated for this project</p>
              </div>
            </div>
          )}
        </>
      )}

      {!selectedId && !loading && (
        <div className="deliverables-empty">
          <span className="material-symbols-outlined deliverables-empty-icon">assignment_turned_in</span>
          <p className="deliverables-empty-text">Select a project to generate deliverables</p>
        </div>
      )}
    </div>
  );
}

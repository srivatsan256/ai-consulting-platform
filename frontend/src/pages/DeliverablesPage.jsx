import React, { useState, useEffect } from "react";
import { projectService, deliverableService } from "../services/api";
import TopHeader from "../components/TopHeader";

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
      <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
        <select
          value={selectedId}
          onChange={(e) => handleProjectSelect(e.target.value)}
          className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {deliverableTypes.map((item) => (
              <div key={item.title} className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-5">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${item.color}`}>
                  <span className="material-symbols-outlined text-[22px]">{item.icon}</span>
                </div>
                <h4 className="font-semibold text-on-surface text-sm mt-3">{item.title}</h4>
                <p className="text-xs text-on-surface-variant mt-0.5">{item.desc}</p>
              </div>
            ))}
          </div>

          {/* Generate Button */}
          <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-8 text-center">
            <span className="material-symbols-outlined text-[48px] text-primary">auto_awesome</span>
            <h4 className="font-headline-sm text-lg font-bold text-on-surface mt-3">Generate All Deliverables</h4>
            <p className="text-on-surface-variant text-sm mt-1 max-w-md mx-auto">
              AI will generate BRD, FRD, PRD, verification summary, project timeline, and metadata as a downloadable ZIP.
            </p>
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="mt-6 px-8 py-3 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 disabled:opacity-50 transition-all flex items-center gap-2 mx-auto shadow-lg shadow-primary/20"
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
            <div className="bg-emerald-50 rounded-xl border border-emerald-200 p-6 flex items-center gap-4">
              <span className="material-symbols-outlined text-emerald-600 text-[32px]" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
              <div className="flex-1">
                <p className="text-sm font-bold text-emerald-800">Deliverables Generated Successfully</p>
                <p className="text-xs text-emerald-600">All documents have been packaged into a ZIP file</p>
              </div>
              <a
                href={zipUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="px-5 py-2.5 bg-emerald-600 text-white rounded-xl font-bold text-sm hover:bg-emerald-700 transition-all flex items-center gap-2"
              >
                <span className="material-symbols-outlined text-[18px]">download</span>
                Download ZIP
              </a>
            </div>
          )}

          {/* Project Status */}
          {project?.status === "COMPLETED" && (
            <div className="bg-blue-50 rounded-xl border border-blue-200 p-6 flex items-center gap-4">
              <span className="material-symbols-outlined text-blue-600 text-[32px]" style={{ fontVariationSettings: "'FILL' 1" }}>info</span>
              <div>
                <p className="text-sm font-bold text-blue-800">Project Completed</p>
                <p className="text-xs text-blue-600">All deliverables have been generated for this project</p>
              </div>
            </div>
          )}
        </>
      )}

      {!selectedId && !loading && (
        <div className="text-center py-16">
          <span className="material-symbols-outlined text-[56px] text-outline-variant">assignment_turned_in</span>
          <p className="text-on-surface-variant mt-3 text-sm">Select a project to generate deliverables</p>
        </div>
      )}
    </div>
  );
}

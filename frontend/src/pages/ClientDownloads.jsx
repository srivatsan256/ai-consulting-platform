import React, { useState, useEffect } from "react";
import { projectService, deliverableService } from "../services/api";
import TopHeader from "../components/TopHeader";

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
      <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
        <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-2">
          Select Project
        </label>
        <select
          value={selectedId}
          onChange={(e) => handleProjectSelect(e.target.value)}
          className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
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
        <div className="text-center py-16">
          <span className="material-symbols-outlined text-[56px] text-outline-variant">download</span>
          <p className="text-on-surface-variant mt-3 text-sm">Select a project to download documents and deliverables</p>
        </div>
      )}

      {selectedId && project && (
        <div className="space-y-6">
          {/* Documents */}
          <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-headline-sm text-base font-bold text-on-surface">Project Documents</h3>
              <span className="text-xs text-on-surface-variant">{project.documents?.length || 0} uploaded</span>
            </div>
            {project.documents?.length ? (
              <div className="space-y-2">
                {project.documents.map((doc) => (
                  <div key={doc.id} className="flex items-center gap-3 p-3 rounded-lg border border-outline-variant/10">
                    <span className="material-symbols-outlined text-primary text-[20px]">description</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-on-surface truncate">{doc.original_name}</p>
                      <p className="text-xs text-on-surface-variant">
                        {doc.doc_type} · Level {doc.level} ·{" "}
                        {doc.verification_status ? "Verified" : "Pending verification"}
                      </p>
                    </div>
                    <button
                      onClick={() => downloadUrl(doc.file_url)}
                      disabled={!doc.file_url}
                      className="px-3 py-1.5 rounded-lg text-xs font-medium border border-outline-variant/30 text-on-surface-variant hover:bg-surface-container disabled:opacity-40 flex items-center gap-1"
                    >
                      <span className="material-symbols-outlined text-[14px]">download</span>
                      Download
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-on-surface-variant text-center py-8">No documents uploaded yet</p>
            )}
          </div>

          {/* Deliverables */}
          <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-8 text-center">
            <span className="material-symbols-outlined text-[48px] text-primary">assignment_turned_in</span>
            <h4 className="font-headline-sm text-lg font-bold text-on-surface mt-3">Project Deliverables</h4>
            <p className="text-on-surface-variant text-sm mt-1 max-w-md mx-auto">
              BRD, FRD, PRD, verification summary, project timeline and metadata packaged as a ZIP.
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
              {generating ? "Generating Deliverables..." : "Generate Deliverables ZIP"}
            </button>

            {zipUrl && (
              <div className="mt-6 p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center gap-4 text-left">
                <span className="material-symbols-outlined text-emerald-600 text-[28px]" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                <div className="flex-1">
                  <p className="text-sm font-bold text-emerald-800">Deliverables ready</p>
                  <p className="text-xs text-emerald-600">Your ZIP package is available to download</p>
                </div>
                <a
                  href={zipUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2.5 bg-emerald-600 text-white rounded-xl font-bold text-sm hover:bg-emerald-700 transition-all flex items-center gap-2"
                >
                  <span className="material-symbols-outlined text-[16px]">download</span>
                  Download ZIP
                </a>
              </div>
            )}
          </div>

          {/* Verification Summary */}
          {project.verification_report && (
            <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
              <h3 className="font-headline-sm text-base font-bold text-on-surface mb-4">Verification Summary</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-surface-container-low">
                  <p className="text-[11px] uppercase tracking-wider text-on-surface-variant">Readiness Score</p>
                  <p className="mt-2 text-2xl font-bold text-on-surface">{project.readiness_score}%</p>
                </div>
                <div className="p-4 rounded-xl bg-surface-container-low">
                  <p className="text-[11px] uppercase tracking-wider text-on-surface-variant">Current Level</p>
                  <p className="mt-2 text-2xl font-bold text-on-surface">L{Math.max(1, project.current_level || 1)}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

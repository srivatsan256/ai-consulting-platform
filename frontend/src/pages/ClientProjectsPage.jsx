import React, { useState, useEffect } from "react";
import { projectService } from "../services/api";
import TopHeader from "../components/TopHeader";

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
          <span className="material-symbols-outlined text-[56px] text-outline-variant">folder_open</span>
          <p className="text-on-surface-variant mt-3 text-sm">Select a project to view its details</p>
        </div>
      )}

      {selectedId && detailLoading && (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {selectedId && project && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
            <div className="flex flex-wrap items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                <span className="material-symbols-outlined text-primary">folder</span>
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-headline-sm text-lg font-bold text-on-surface">{project.project_name}</h3>
                <p className="text-xs text-on-surface-variant mt-0.5">
                  {project.company_name} · {project.industry || "General"}
                </p>
              </div>
              <div className="flex items-center gap-2">
                {project.readiness_score != null && (
                  <span className={`px-3 py-1.5 rounded-lg text-xs font-bold ${
                    project.readiness_score >= 90 ? "bg-emerald-100 text-emerald-700" : project.readiness_score >= 70 ? "bg-amber-100 text-amber-700" : "bg-red-100 text-red-700"
                  }`}>
                    {project.readiness_score}% ready
                  </span>
                )}
                <span className={`px-3 py-1.5 rounded-lg text-xs font-bold ${STATUS_COLORS[project.status] || "bg-gray-100 text-gray-600"}`}>
                  {project.status}
                </span>
              </div>
            </div>
            <div className="mt-4 w-full h-2 bg-surface-container rounded-full overflow-hidden">
              <div className="h-full bg-primary rounded-full" style={{ width: `${project.readiness_score || 0}%` }} />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-5">
              <div>
                <p className="text-[11px] uppercase tracking-wider text-on-surface-variant mb-1">Current Level</p>
                <p className="text-sm font-bold text-on-surface">L{Math.max(1, project.current_level || 1)}</p>
              </div>
              <div>
                <p className="text-[11px] uppercase tracking-wider text-on-surface-variant mb-1">Documents</p>
                <p className="text-sm font-bold text-on-surface">{project.documents?.length || 0}</p>
              </div>
              <div>
                <p className="text-[11px] uppercase tracking-wider text-on-surface-variant mb-1">Expected Timeline</p>
                <p className="text-sm font-bold text-on-surface">{project.expected_timeline || "N/A"}</p>
              </div>
            </div>
          </div>

          {/* Objectives */}
          {project.objectives && (
            <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
              <h4 className="font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-2">Objectives</h4>
              <p className="text-sm text-on-surface leading-relaxed">{project.objectives}</p>
            </div>
          )}

          {/* Documents */}
          <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-headline-sm text-base font-bold text-on-surface">Documents</h3>
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
                        {doc.doc_type} · Level {doc.level} · Uploaded {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : "N/A"}
                      </p>
                    </div>
                    <span className={`px-2 py-1 rounded text-[10px] font-bold ${
                      doc.verification_status ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"
                    }`}>
                      {doc.verification_status ? "Passed" : "Pending"}
                    </span>
                    <button
                      onClick={() => openDocument(doc.file_url)}
                      disabled={!doc.file_url}
                      className="px-3 py-1.5 rounded-lg text-xs font-medium border border-outline-variant/30 text-on-surface-variant hover:bg-surface-container disabled:opacity-40 flex items-center gap-1"
                    >
                      <span className="material-symbols-outlined text-[14px]">open_in_new</span>
                      View
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-on-surface-variant text-center py-8">No documents uploaded yet</p>
            )}
          </div>

          {/* Verification Report */}
          {reportResults.length > 0 && (
            <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
              <h3 className="font-headline-sm text-base font-bold text-on-surface mb-4">Verification Report</h3>
              <div className="space-y-3">
                {reportResults.map((result, idx) => (
                  <div key={idx} className="p-4 rounded-xl border border-outline-variant/20">
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`w-2 h-2 rounded-full ${result.passed ? "bg-emerald-500" : "bg-red-500"}`} />
                      <span className="font-semibold text-on-surface text-sm">{result.doc_type} Document</span>
                      <span className={`ml-auto px-3 py-1 rounded-lg text-xs font-bold ${
                        result.passed ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"
                      }`}>
                        {result.score}%
                      </span>
                    </div>
                    {result.evidence && (
                      <p className="text-xs text-on-surface-variant p-3 rounded-lg bg-surface-container-low leading-relaxed">{result.evidence}</p>
                    )}
                    {result.ai_feedback && (
                      <p className="text-xs text-on-surface-variant mt-2 p-2 bg-blue-50 rounded-lg">{result.ai_feedback}</p>
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

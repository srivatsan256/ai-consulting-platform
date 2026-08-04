import React, { useState, useEffect } from "react";
import { projectService } from "../services/api";
import TopHeader from "../components/TopHeader";

export default function ReportsPage({ projectId, onSelectProject }) {
  const [projects, setProjects] = useState([]);
  const [selectedId, setSelectedId] = useState(projectId || "");
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);

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
    if (id) fetchProject(id);
  };

  const report = project?.verification_report;
  const reportData = report?.report_data;
  const reportDocuments = report?.results || reportData?.documents || [];

  return (
    <div className="space-y-6">
      <TopHeader title="Reports" subtitle="Verification and project reports" />

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

      {selectedId && project && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-xl soft-shadow border border-outline-variant/20">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <span className="material-symbols-outlined text-primary text-[22px]">analytics</span>
                </div>
                <div>
                  <p className="text-xl font-bold text-on-surface">{project.readiness_score ?? "N/A"}%</p>
                  <p className="text-xs text-on-surface-variant">Readiness Score</p>
                </div>
              </div>
            </div>
            <div className="bg-white p-5 rounded-xl soft-shadow border border-outline-variant/20">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
                  <span className="material-symbols-outlined text-blue-600 text-[22px]">description</span>
                </div>
                <div>
                  <p className="text-xl font-bold text-on-surface">{project.documents?.length || 0}</p>
                  <p className="text-xs text-on-surface-variant">Documents</p>
                </div>
              </div>
            </div>
            <div className="bg-white p-5 rounded-xl soft-shadow border border-outline-variant/20">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center">
                  <span className="material-symbols-outlined text-emerald-600 text-[22px]">check_circle</span>
                </div>
                <div>
                  <p className="text-xl font-bold text-on-surface">{reportDocuments?.filter(d => d.passed).length || 0}</p>
                  <p className="text-xs text-on-surface-variant">Passed</p>
                </div>
              </div>
            </div>
            <div className="bg-white p-5 rounded-xl soft-shadow border border-outline-variant/20">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-red-50 flex items-center justify-center">
                  <span className="material-symbols-outlined text-red-600 text-[22px]">cancel</span>
                </div>
                <div>
                  <p className="text-xl font-bold text-on-surface">{reportDocuments?.filter(d => !d.passed).length || 0}</p>
                  <p className="text-xs text-on-surface-variant">Failed</p>
                </div>
              </div>
            </div>
          </div>

          {/* Verification Report */}
          {reportDocuments.length > 0 ? (
            <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
              <h3 className="font-headline-sm text-base font-semibold text-on-surface mb-4">Verification Report</h3>
              <p className="text-xs text-on-surface-variant mb-4">Generated: {report?.generated_at ? new Date(report.generated_at).toLocaleString() : "N/A"}</p>
              <div className="space-y-4">
                {reportDocuments.map((doc, idx) => (
                  <div key={idx} className="p-4 rounded-xl border border-outline-variant/20">
                    <div className="flex items-center gap-3 mb-3">
                      <span className={`w-3 h-3 rounded-full ${doc.passed ? "bg-emerald-500" : "bg-red-500"}`} />
                      <span className="font-semibold text-on-surface text-sm">{doc.doc_type} Document</span>
                      <span className={`ml-auto px-3 py-1 rounded-lg text-xs font-bold ${
                        doc.passed ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"
                      }`}>
                        {doc.score}%
                      </span>
                    </div>
                    <div className="w-full h-2 bg-surface-container rounded-full overflow-hidden mb-3">
                      <div
                        className={`h-full rounded-full ${doc.passed ? "bg-emerald-500" : "bg-red-500"}`}
                        style={{ width: `${doc.score}%` }}
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-xs">
                      <div>
                        <p className="text-on-surface-variant font-medium mb-1">Missing Keywords</p>
                        {doc.missing_keywords?.length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {doc.missing_keywords.map((kw, i) => (
                              <span key={i} className="px-2 py-0.5 bg-red-50 text-red-600 rounded">{kw}</span>
                            ))}
                          </div>
                        ) : (
                          <span className="text-emerald-600">None</span>
                        )}
                      </div>
                      <div>
                        <p className="text-on-surface-variant font-medium mb-1">Missing Sections</p>
                        {doc.missing_sections?.length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {doc.missing_sections.map((sec, i) => (
                              <span key={i} className="px-2 py-0.5 bg-amber-50 text-amber-600 rounded">{sec}</span>
                            ))}
                          </div>
                        ) : (
                          <span className="text-emerald-600">None</span>
                        )}
                      </div>
                    </div>
                    {doc.ai_feedback && (
                      <div className="mt-3 p-2 bg-blue-50 rounded-lg">
                        <p className="text-xs text-blue-800">{doc.ai_feedback}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-16">
              <span className="material-symbols-outlined text-[56px] text-outline-variant">analytics</span>
              <p className="text-on-surface-variant mt-3 text-sm">
                {project.documents?.length ? "Run verification to generate a report" : "Upload documents and run verification first"}
              </p>
            </div>
          )}
        </>
      )}

      {!selectedId && !loading && (
        <div className="text-center py-16">
          <span className="material-symbols-outlined text-[56px] text-outline-variant">analytics</span>
          <p className="text-on-surface-variant mt-3 text-sm">Select a project to view reports</p>
        </div>
      )}
    </div>
  );
}

import React, { useState, useEffect } from "react";
import { projectService } from "../services/api";
import TopHeader from "../components/TopHeader";
import "./ReportsPage.css";

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
      <div className="reports-card soft-shadow">
        <select
          value={selectedId}
          onChange={(e) => handleProjectSelect(e.target.value)}
          className="reports-select"
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
          <div className="reports-summary-grid">
            <div className="reports-summary-card soft-shadow">
              <div className="reports-summary-inner">
                <div className="reports-summary-icon bg-primary/10 text-primary">
                  <span className="material-symbols-outlined">analytics</span>
                </div>
                <div>
                  <p className="reports-summary-value">{project.readiness_score ?? "N/A"}%</p>
                  <p className="reports-summary-label">Readiness Score</p>
                </div>
              </div>
            </div>
            <div className="reports-summary-card soft-shadow">
              <div className="reports-summary-inner">
                <div className="reports-summary-icon bg-blue-50 text-blue-600">
                  <span className="material-symbols-outlined">description</span>
                </div>
                <div>
                  <p className="reports-summary-value">{project.documents?.length || 0}</p>
                  <p className="reports-summary-label">Documents</p>
                </div>
              </div>
            </div>
            <div className="reports-summary-card soft-shadow">
              <div className="reports-summary-inner">
                <div className="reports-summary-icon bg-emerald-50 text-emerald-600">
                  <span className="material-symbols-outlined">check_circle</span>
                </div>
                <div>
                  <p className="reports-summary-value">{reportDocuments?.filter(d => d.passed).length || 0}</p>
                  <p className="reports-summary-label">Passed</p>
                </div>
              </div>
            </div>
            <div className="reports-summary-card soft-shadow">
              <div className="reports-summary-inner">
                <div className="reports-summary-icon bg-red-50 text-red-600">
                  <span className="material-symbols-outlined">cancel</span>
                </div>
                <div>
                  <p className="reports-summary-value">{reportDocuments?.filter(d => !d.passed).length || 0}</p>
                  <p className="reports-summary-label">Failed</p>
                </div>
              </div>
            </div>
          </div>

          {/* Verification Report */}
          {reportDocuments.length > 0 ? (
            <div className="reports-report-card soft-shadow">
              <h3 className="reports-report-title">Verification Report</h3>
              <p className="reports-generated">Generated: {report?.generated_at ? new Date(report.generated_at).toLocaleString() : "N/A"}</p>
              <div className="space-y-4">
                {reportDocuments.map((doc, idx) => (
                  <div key={idx} className="reports-doc-card">
                    <div className="reports-doc-header">
                      <span className={`reports-doc-dot ${doc.passed ? "bg-emerald-500" : "bg-red-500"}`} />
                      <span className="reports-doc-title">{doc.doc_type} Document</span>
                      <span className={`reports-doc-score ${
                        doc.passed ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"
                      }`}>
                        {doc.score}%
                      </span>
                    </div>
                    <div className="reports-score-track">
                      <div
                        className={`reports-score-fill ${doc.passed ? "bg-emerald-500" : "bg-red-500"}`}
                        style={{ width: `${doc.score}%` }}
                      />
                    </div>
                    <div className="reports-missing-grid">
                      <div>
                        <p className="reports-missing-label">Missing Keywords</p>
                        {doc.missing_keywords?.length > 0 ? (
                          <div className="reports-chip-wrap">
                            {doc.missing_keywords.map((kw, i) => (
                              <span key={i} className="reports-chip-red">{kw}</span>
                            ))}
                          </div>
                        ) : (
                          <span className="reports-none">None</span>
                        )}
                      </div>
                      <div>
                        <p className="reports-missing-label">Missing Sections</p>
                        {doc.missing_sections?.length > 0 ? (
                          <div className="reports-chip-wrap">
                            {doc.missing_sections.map((sec, i) => (
                              <span key={i} className="reports-chip-amber">{sec}</span>
                            ))}
                          </div>
                        ) : (
                          <span className="reports-none">None</span>
                        )}
                      </div>
                    </div>
                    {doc.ai_feedback && (
                      <div className="reports-ai">
                        <p className="reports-ai-text">{doc.ai_feedback}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="reports-empty">
              <span className="material-symbols-outlined reports-empty-icon">analytics</span>
              <p className="reports-empty-text">
                {project.documents?.length ? "Run verification to generate a report" : "Upload documents and run verification first"}
              </p>
            </div>
          )}
        </>
      )}

      {!selectedId && !loading && (
        <div className="reports-empty">
          <span className="material-symbols-outlined reports-empty-icon">analytics</span>
          <p className="reports-empty-text">Select a project to view reports</p>
        </div>
      )}
    </div>
  );
}

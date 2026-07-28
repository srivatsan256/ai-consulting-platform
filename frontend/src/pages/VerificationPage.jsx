import React, { useState, useEffect } from "react";
import { projectService, verificationService } from "../services/api";
import TopHeader from "../components/TopHeader";

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
          results: res.data.verification_report.report_data?.documents || [],
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
      <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
        <div className="flex flex-col sm:flex-row gap-3">
          <select
            value={selectedId}
            onChange={(e) => handleProjectSelect(e.target.value)}
            className="flex-1 px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
          >
            <option value="">Select a project</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>{p.project_name} ({p.company_name})</option>
            ))}
          </select>
          <label className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-outline-variant/40 text-sm text-on-surface-variant cursor-pointer">
            <input
              type="checkbox"
              checked={useAi}
              onChange={(e) => setUseAi(e.target.checked)}
              className="rounded border-outline-variant text-primary focus:ring-primary"
            />
            AI Analysis
          </label>
          <button
            onClick={handleVerify}
            disabled={!selectedId || verifying || !project?.documents?.length}
            className="px-5 py-2.5 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 disabled:opacity-50 transition-all flex items-center gap-2 shadow-lg shadow-primary/20"
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
        <div className="text-center py-16">
          <span className="material-symbols-outlined text-[56px] text-outline-variant">verified_user</span>
          <p className="text-on-surface-variant mt-3 text-sm">Select a project to run document verification</p>
        </div>
      )}

      {/* Project with no documents */}
      {selectedId && project && (!project.documents || project.documents.length === 0) && (
        <div className="text-center py-16">
          <span className="material-symbols-outlined text-[56px] text-outline-variant">upload_file</span>
          <p className="text-on-surface-variant mt-3 text-sm">No documents uploaded for this project</p>
          <button
            onClick={() => onSelectProject(selectedId)}
            className="mt-4 px-4 py-2 bg-primary text-on-primary rounded-lg text-sm font-medium hover:opacity-90"
          >
            Upload Documents
          </button>
        </div>
      )}

      {/* Verification Results */}
      {result && (
        <div className="space-y-4">
          {/* Readiness Score Card */}
          <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
            <div className="flex items-center gap-4">
              <div className={`w-16 h-16 rounded-2xl flex items-center justify-center ${
                result.readiness_score >= 90 ? "bg-emerald-100" : result.readiness_score >= 70 ? "bg-amber-100" : "bg-red-100"
              }`}>
                <span className={`text-2xl font-bold ${
                  result.readiness_score >= 90 ? "text-emerald-700" : result.readiness_score >= 70 ? "text-amber-700" : "text-red-700"
                }`}>
                  {result.readiness_score}%
                </span>
              </div>
              <div>
                <h3 className="font-headline-sm text-lg font-bold text-on-surface">Readiness Score</h3>
                <p className="text-sm text-on-surface-variant">
                  {result.readiness_score >= 90
                    ? "Documents meet readiness threshold. Ready for next phase."
                    : "Documents need improvement. Review missing items below."}
                </p>
              </div>
              <div className={`ml-auto px-4 py-2 rounded-xl text-sm font-bold ${
                result.readiness_score >= 90
                  ? "bg-emerald-100 text-emerald-700"
                  : "bg-amber-100 text-amber-700"
              }`}>
                {result.readiness_score >= 90 ? "Ready" : "Needs Work"}
              </div>
            </div>
            {/* Progress bar */}
            <div className="mt-4 w-full h-3 bg-surface-container rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  result.readiness_score >= 90 ? "bg-emerald-500" : result.readiness_score >= 70 ? "bg-amber-500" : "bg-red-500"
                }`}
                style={{ width: `${result.readiness_score}%` }}
              />
            </div>
          </div>

          {/* Document Results */}
          {result.results?.map((docResult, idx) => (
            <div key={idx} className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
              <div className="flex items-center gap-3 mb-4">
                <span className={`w-3 h-3 rounded-full ${docResult.passed ? "bg-emerald-500" : "bg-red-500"}`} />
                <h4 className="font-semibold text-on-surface">{docResult.doc_type} Document</h4>
                <span className={`ml-auto px-3 py-1 rounded-lg text-xs font-bold ${
                  docResult.passed ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"
                }`}>
                  {docResult.score}%
                </span>
              </div>

              {/* Score bar */}
              <div className="w-full h-2 bg-surface-container rounded-full overflow-hidden mb-4">
                <div
                  className={`h-full rounded-full ${docResult.passed ? "bg-emerald-500" : "bg-red-500"}`}
                  style={{ width: `${docResult.score}%` }}
                />
              </div>

              {/* Missing Keywords */}
              {docResult.missing_keywords?.length > 0 && (
                <div className="mb-3">
                  <p className="text-xs font-bold text-red-600 uppercase tracking-wider mb-2">Missing Keywords</p>
                  <div className="flex flex-wrap gap-2">
                    {docResult.missing_keywords.map((kw, i) => (
                      <span key={i} className="px-2 py-1 bg-red-50 text-red-700 rounded text-xs font-medium border border-red-200">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Missing Sections */}
              {docResult.missing_sections?.length > 0 && (
                <div className="mb-3">
                  <p className="text-xs font-bold text-amber-600 uppercase tracking-wider mb-2">Missing Sections</p>
                  <div className="flex flex-wrap gap-2">
                    {docResult.missing_sections.map((sec, i) => (
                      <span key={i} className="px-2 py-1 bg-amber-50 text-amber-700 rounded text-xs font-medium border border-amber-200">
                        {sec}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* AI Feedback */}
              {docResult.ai_feedback && (
                <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-xs font-bold text-blue-700 mb-1">AI Analysis</p>
                  <p className="text-xs text-blue-800 leading-relaxed">{docResult.ai_feedback}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {selectedId && project && project.documents?.length > 0 && !result && !verifying && (
        <div className="text-center py-12">
          <span className="material-symbols-outlined text-[48px] text-outline-variant">rate_review</span>
          <p className="text-on-surface-variant mt-3 text-sm">Click "Run Verification" to analyze {project.documents.length} document(s)</p>
        </div>
      )}
    </div>
  );
}

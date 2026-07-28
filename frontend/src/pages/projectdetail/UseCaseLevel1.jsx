import React, { useState, useEffect } from "react";
import TopHeader from "../../components/TopHeader";
import { projectService } from "../../services/api";

const STATUS_COLORS = {
  DISCOVERY: "bg-blue-100 text-blue-700",
  VERIFICATION: "bg-amber-100 text-amber-700",
  PROCESSING: "bg-purple-100 text-purple-700",
  REVIEW: "bg-indigo-100 text-indigo-700",
  COMPLETED: "bg-emerald-100 text-emerald-700",
};

const TABS = [
  { id: "overview", label: "Overview", icon: "info" },
  { id: "verification", label: "Upload Documents", icon: "verified_user" },
  { id: "use-case-level1", label: "Use Case Level 1", icon: "description" },
  { id: "use-case-evaluation-sheet-level1", label: "Evaluation Sheet", icon: "assessment" },
  { id: "use-case-shortlisting-report-level1", label: "Shortlisting Report", icon: "summarize" },
];

export default function UseCaseLevel1({ projectId, onBack, onNavigate }) {
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    department: "",
    problemStatement: "",
    expectedOutcomes: "",
    dataSources: "",
    painPoints: "",
    referenceMaterial: "none",
  });

  useEffect(() => {
    if (projectId) fetchProject();
  }, [projectId]);

  const fetchProject = async () => {
    try {
      const res = await projectService.get(projectId);
      setProject(res.data);
    } catch (err) {
      console.error("Failed to fetch project:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = () => {
    console.log("Generating Use Case Document with data:", formData);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const currentLevel = Math.max(1, project?.current_level || 1);
  const readinessLabel = project?.readiness_score != null ? `${Math.round(project.readiness_score)}%` : "N/A";

  return (
    <div className="space-y-6">
      <TopHeader
        title={project?.project_name || "Project"}
        subtitle={project?.company_name}
        actions={
          <button
            onClick={onBack}
            className="px-4 py-2 rounded-xl border border-outline-variant/40 text-on-surface-variant text-sm font-medium hover:bg-surface-container transition-colors flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-[18px]">arrow_back</span>
            Back
          </button>
        }
      />

      {/* Status Bar */}
      <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-4 flex flex-wrap items-center gap-4">
        <span className={`px-3 py-1.5 rounded-lg text-xs font-bold ${STATUS_COLORS[project?.status] || "bg-gray-100 text-gray-600"}`}>
          {project?.status}
        </span>
        <span className="text-xs text-on-surface-variant flex items-center gap-1">
          <span className="material-symbols-outlined text-[14px]">numbers</span>
          Current Level L{currentLevel}
        </span>
        {project?.expected_timeline && (
          <span className="text-xs text-on-surface-variant flex items-center gap-1">
            <span className="material-symbols-outlined text-[14px]">schedule</span>
            {project.expected_timeline}
          </span>
        )}
        <span className="text-xs text-on-surface-variant flex items-center gap-1">
          <span className="material-symbols-outlined text-[14px]">description</span>
          {project?.documents?.length || 0} documents
        </span>
        <div className="flex items-center gap-2 ml-auto">
          <div className="px-3 py-1.5 rounded-lg bg-surface-container-low text-xs text-on-surface-variant flex items-center gap-2">
            <span className="material-symbols-outlined text-[14px] text-primary">layers</span>
            {project?.completed_levels?.length || 0} levels complete
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-surface-container-low text-xs text-on-surface-variant flex items-center gap-2">
            <span className="material-symbols-outlined text-[14px] text-primary">verified_user</span>
            Readiness {readinessLabel}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-white rounded-xl soft-shadow border border-outline-variant/20 p-1 overflow-x-auto">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onNavigate(tab.id)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
              tab.id === "use-case-level1"
                ? "bg-primary text-on-primary shadow-sm"
                : "text-on-surface-variant hover:bg-surface-container"
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
        <div className="space-y-6">
          <div>
            <h3 className="font-headline-sm text-base font-bold text-on-surface">
              Create Use Case Document
            </h3>
            <p className="text-xs text-on-surface-variant mt-1">
              Provide the context below. The system will generate a detailed Use Case Document for the organisation.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-5">
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1.5 uppercase tracking-wider">
                Department
              </label>
              <input
                type="text"
                value={formData.department}
                onChange={(e) => setFormData((prev) => ({ ...prev, department: e.target.value }))}
                placeholder="e.g. Finance, Operations, Customer Success"
                className="w-full rounded-lg border border-outline-variant/30 bg-surface-container-low/30 px-3 py-2.5 text-sm text-on-surface placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1.5 uppercase tracking-wider">
                Problem Statement
              </label>
              <textarea
                value={formData.problemStatement}
                onChange={(e) => setFormData((prev) => ({ ...prev, problemStatement: e.target.value }))}
                placeholder="Brief description of the problem this project aims to solve..."
                rows={4}
                className="w-full rounded-lg border border-outline-variant/30 bg-surface-container-low/30 p-3 text-sm text-on-surface placeholder:text-outline resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1.5 uppercase tracking-wider">
                Expected Outcomes (Business Impact)
              </label>
              <textarea
                value={formData.expectedOutcomes}
                onChange={(e) => setFormData((prev) => ({ ...prev, expectedOutcomes: e.target.value }))}
                placeholder="Describe the expected business impact, KPIs, and success metrics..."
                rows={3}
                className="w-full rounded-lg border border-outline-variant/30 bg-surface-container-low/30 p-3 text-sm text-on-surface placeholder:text-outline resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1.5 uppercase tracking-wider">
                Data Sources
              </label>
              <textarea
                value={formData.dataSources}
                onChange={(e) => setFormData((prev) => ({ ...prev, dataSources: e.target.value }))}
                placeholder={"One source per line\ne.g. CRM system\nERP reports\nCustomer support tickets"}
                rows={3}
                className="w-full rounded-lg border border-outline-variant/30 bg-surface-container-low/30 p-3 text-sm text-on-surface placeholder:text-outline resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50"
              />
              <p className="text-[11px] text-on-surface-variant mt-1">Enter one item per line</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1.5 uppercase tracking-wider">
                Pain Points & Current Process Gaps
              </label>
              <textarea
                value={formData.painPoints}
                onChange={(e) => setFormData((prev) => ({ ...prev, painPoints: e.target.value }))}
                placeholder={"One pain point per line\ne.g. Manual data entry causes delays\nNo single source of truth for inventory"}
                rows={4}
                className="w-full rounded-lg border border-outline-variant/30 bg-surface-container-low/30 p-3 text-sm text-on-surface placeholder:text-outline resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50"
              />
              <p className="text-[11px] text-on-surface-variant mt-1">Enter one item per line</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1.5 uppercase tracking-wider">
                Reference Material
              </label>
              <input
                type="text"
                value={formData.referenceMaterial}
                onChange={(e) => setFormData((prev) => ({ ...prev, referenceMaterial: e.target.value }))}
                placeholder='Attach document names or type "none"'
                className="w-full rounded-lg border border-outline-variant/30 bg-surface-container-low/30 px-3 py-2.5 text-sm text-on-surface placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50"
              />
            </div>
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={handleGenerate}
              disabled={!formData.department || !formData.problemStatement}
              className="px-5 py-2.5 bg-primary text-on-primary rounded-xl text-sm font-bold hover:opacity-90 disabled:opacity-50 transition-all flex items-center gap-2 shadow-lg shadow-primary/20"
            >
              <span className="material-symbols-outlined text-[18px]">auto_awesome</span>
              Generate Use Case Document
            </button>
            <button
              onClick={() => setFormData({ department: "", problemStatement: "", expectedOutcomes: "", dataSources: "", painPoints: "", referenceMaterial: "none" })}
              className="px-4 py-2.5 rounded-xl border border-outline-variant/40 text-on-surface-variant text-sm font-medium hover:bg-surface-container transition-colors"
            >
              Clear Form
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

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

export default function UseCaseEvaluationSheetLevel1({ projectId, onBack, onNavigate }) {
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    useCaseName: "",
    department: "",
    dataAvailability: 3,
    managementPriority: 3,
    thirdPartyDependency: 3,
    feasibilityROI: 3,
    operationalReadiness: 3,
    dependencies: "",
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

  const calculateWeightedScore = () => {
    const weights = {
      dataAvailability: 0.25,
      managementPriority: 0.30,
      thirdPartyDependency: 0.20,
      feasibilityROI: 0.15,
      operationalReadiness: 0.10,
    };
    const total = (
      formData.dataAvailability * weights.dataAvailability +
      formData.managementPriority * weights.managementPriority +
      formData.thirdPartyDependency * weights.thirdPartyDependency +
      formData.feasibilityROI * weights.feasibilityROI +
      formData.operationalReadiness * weights.operationalReadiness
    ) * 100;
    return Math.round(total);
  };

  const getRecommendation = (score) => {
    if (score >= 80) return "Proceed";
    if (score >= 60) return "Defer";
    if (score >= 40) return "Re-evaluate later";
    return "Reject";
  };

  const renderScoreInputs = (label, value, onChange, min = 1, max = 5) => {
    return (
      <div className="space-y-2">
        <label className="block text-xs font-semibold text-on-surface-variant uppercase tracking-wider">
          {label} ({min}-{max}) {value > 0 && `Score: ${value}`}
        </label>
        <input
          type="range"
          min={min}
          max={max}
          value={value}
          onChange={onChange}
          className="w-full h-2 bg-surface-container rounded-lg appearance-none cursor-pointer"
        />
        <div className="flex justify-between text-[10px] text-on-surface-variant">
          <span>Poor</span>
          <span>Fair</span>
          <span>Good</span>
          <span>Excellent</span>
          <span>Outstanding</span>
        </div>
      </div>
    );
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
              tab.id === "use-case-evaluation-sheet-level1"
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
              Use Case Evaluation Sheet
            </h3>
            <p className="text-xs text-on-surface-variant mt-1">
              Evaluate the use case based on the criteria below to determine its feasibility and priority.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-5">
            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1.5 uppercase tracking-wider">
                Use Case Name
              </label>
              <input
                type="text"
                value={formData.useCaseName}
                onChange={(e) => setFormData((prev) => ({ ...prev, useCaseName: e.target.value }))}
                placeholder="Enter use case name..."
                className="w-full rounded-lg border border-outline-variant/30 bg-surface-container-low/30 px-3 py-2.5 text-sm text-on-surface placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50"
              />
            </div>

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

            <div className="space-y-4">
              <h4 className="font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-3">
                Evaluation Criteria
              </h4>

              {renderScoreInputs("Data Availability", formData.dataAvailability, (e) =>
                setFormData((prev) => ({ ...prev, dataAvailability: parseInt(e.target.value) }))
              )}
              <p className="text-[10px] text-on-surface-variant ml-1">
                Evaluate data availability, accessibility, cleanliness, and preprocessing needs
              </p>

              {renderScoreInputs("Management Priority", formData.managementPriority, (e) =>
                setFormData((prev) => ({ ...prev, managementPriority: parseInt(e.target.value) }))
              )}
              <p className="text-[10px] text-on-surface-variant ml-1">
                Evaluate leadership interest, strategic alignment, and budget availability
              </p>

              {renderScoreInputs("Third-Party Dependency", formData.thirdPartyDependency, (e) =>
                setFormData((prev) => ({ ...prev, thirdPartyDependency: parseInt(e.target.value) }))
              )}
              <p className="text-[10px] text-on-surface-variant ml-1">
                Evaluate existing tools, licensing constraints, and integration limitations
              </p>

              {renderScoreInputs("Feasibility & ROI", formData.feasibilityROI, (e) =>
                setFormData((prev) => ({ ...prev, feasibilityROI: parseInt(e.target.value) }))
              )}
              <p className="text-[10px] text-on-surface-variant ml-1">
                Evaluate development complexity, business impact, and cost vs benefit
              </p>

              {renderScoreInputs("Operational Readiness", formData.operationalReadiness, (e) =>
                setFormData((prev) => ({ ...prev, operationalReadiness: parseInt(e.target.value) }))
              )}
              <p className="text-[10px] text-on-surface-variant ml-1">
                Evaluate team readiness, process maturity, and adoption capability
              </p>
            </div>

            <div className="bg-surface-container/30 rounded-xl p-5">
              <h4 className="font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-3">
                Weighted Scoring Table
              </h4>
              <div className="grid grid-cols-5 gap-3 text-[10px] font-medium text-on-surface-variant border-b border-outline-variant/20 pb-2">
                <div>Criteria</div>
                <div>Score</div>
                <div>Weight</div>
                <div>Weighted Score</div>
                <div>Total</div>
              </div>
              <div className="space-y-2 mt-2">
                <div className="grid grid-cols-5 gap-3 text-[11px] text-on-surface">
                  <div>Data Availability</div>
                  <div>{formData.dataAvailability}/5</div>
                  <div>25%</div>
                  <div>{Math.round(formData.dataAvailability * 25)}</div>
                  <div>{Math.round(formData.dataAvailability * 25)}</div>
                </div>
                <div className="grid grid-cols-5 gap-3 text-[11px] text-on-surface">
                  <div>Management Priority</div>
                  <div>{formData.managementPriority}/5</div>
                  <div>30%</div>
                  <div>{Math.round(formData.managementPriority * 30)}</div>
                  <div>{Math.round(formData.managementPriority * 30)}</div>
                </div>
                <div className="grid grid-cols-5 gap-3 text-[11px] text-on-surface">
                  <div>Third-Party Dependency</div>
                  <div>{formData.thirdPartyDependency}/5</div>
                  <div>20%</div>
                  <div>{Math.round(formData.thirdPartyDependency * 20)}</div>
                  <div>{Math.round(formData.thirdPartyDependency * 20)}</div>
                </div>
                <div className="grid grid-cols-5 gap-3 text-[11px] text-on-surface">
                  <div>Feasibility & ROI</div>
                  <div>{formData.feasibilityROI}/5</div>
                  <div>15%</div>
                  <div>{Math.round(formData.feasibilityROI * 15)}</div>
                  <div>{Math.round(formData.feasibilityROI * 15)}</div>
                </div>
                <div className="grid grid-cols-5 gap-3 text-[11px] text-on-surface">
                  <div>Operational Readiness</div>
                  <div>{formData.operationalReadiness}/5</div>
                  <div>10%</div>
                  <div>{Math.round(formData.operationalReadiness * 10)}</div>
                  <div>{Math.round(formData.operationalReadiness * 10)}</div>
                </div>
                <div className="grid grid-cols-5 gap-3 text-[11px] font-bold text-primary pt-2 border-t border-outline-variant/20">
                  <div>Total</div>
                  <div>-</div>
                  <div>-</div>
                  <div>{calculateWeightedScore()}/100</div>
                  <div>{calculateWeightedScore()}/100</div>
                </div>
              </div>
            </div>

            <div className="bg-blue-50/50 rounded-xl p-5">
              <h4 className="font-label-md text-[11px] uppercase tracking-wider text-blue-600 mb-2">
                Feasibility Summary
              </h4>
              <p className="text-xs text-on-surface">
                Overall feasibility score: <span className="font-bold">{calculateWeightedScore()}/100</span>
              </p>
              <p className="text-xs text-on-surface-variant mt-2">
                Recommendation: <span className="font-bold text-green-600">{getRecommendation(calculateWeightedScore())}</span>
              </p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-on-surface-variant mb-1.5 uppercase tracking-wider">
                Dependencies
              </label>
              <textarea
                value={formData.dependencies}
                onChange={(e) => setFormData((prev) => ({ ...prev, dependencies: e.target.value }))}
                placeholder="List any technical or business dependencies..."
                rows={3}
                className="w-full rounded-lg border border-outline-variant/30 bg-surface-container-low/30 p-3 text-sm text-on-surface placeholder:text-outline resize-none focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50"
              />
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

          <div className="bg-amber-50/50 rounded-xl p-4">
            <h4 className="font-label-md text-[11px] uppercase tracking-wider text-amber-600 mb-2">
              Risks & Assumptions
            </h4>
            <ul className="text-xs text-on-surface space-y-1">
              <li>• Assumption: All data sources are accessible within the project timeline</li>
              <li>• Risk: Third-party integrations may require additional licensing</li>
              <li>• Assumption: Team has required technical expertise</li>
              <li>• Risk: Business priorities may shift during implementation</li>
            </ul>
          </div>

          <div className="bg-surface-container/30 rounded-xl p-4">
            <h4 className="font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-3">
              Approval Sign-Off
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-[10px] font-semibold text-on-surface-variant mb-1.5">
                  Department Head
                </label>
                <div className="h-8 bg-white rounded border border-outline-variant/30 flex items-center px-2 text-[10px] text-on-surface-variant">
                  Signature & Date
                </div>
              </div>
              <div>
                <label className="block text-[10px] font-semibold text-on-surface-variant mb-1.5">
                  Product Owner
                </label>
                <div className="h-8 bg-white rounded border border-outline-variant/30 flex items-center px-2 text-[10px] text-on-surface-variant">
                  Signature & Date
                </div>
              </div>
              <div>
                <label className="block text-[10px] font-semibold text-on-surface-variant mb-1.5">
                  Sponsor
                </label>
                <div className="h-8 bg-white rounded border border-outline-variant/30 flex items-center px-2 text-[10px] text-on-surface-variant">
                  Signature & Date
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              disabled={!formData.useCaseName || !formData.department}
              className="px-5 py-2.5 bg-primary text-on-primary rounded-xl text-sm font-bold hover:opacity-90 disabled:opacity-50 transition-all shadow-lg shadow-primary/20"
            >
              Save Evaluation
            </button>
            <button
              onClick={() => setFormData({ useCaseName: "", department: "", dataAvailability: 3, managementPriority: 3, thirdPartyDependency: 3, feasibilityROI: 3, operationalReadiness: 3, dependencies: "", referenceMaterial: "none" })}
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

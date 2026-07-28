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

export default function UseCaseShortlistingReportLevel1({ projectId, onBack, onNavigate }) {
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    useCases: [],
    businessPriority: "Medium",
    dependencies: "",
    referenceMaterial: "none",
  });

  useEffect(() => {
    if (projectId) fetchProject();
  }, [projectId]);

  useEffect(() => {
    if (formData.useCases.length === 0) {
      generateSampleUseCases();
    }
  }, []);

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

  const generateSampleUseCases = () => {
    const sampleUseCases = [
      {
        id: 1,
        name: "AI-Powered Customer Support Chatbot",
        department: "Customer Success",
        totalScore: 85,
        weightedScore: 82,
        problemStatement: "Manual customer support results in delays and inconsistent responses",
        expectedOutcome: "Reduce response time by 70% and improve customer satisfaction to 90%",
        dataReadiness: "High - CRM data available",
        businessImpact: "Increase CSAT by 15% and reduce support costs by 25%",
        feasibility: "High - Proven technology available",
        risks: ["Integration with existing helpdesk system", "Training data requirements"],
      },
      {
        id: 2,
        name: "Predictive Revenue Forecasting",
        department: "Finance",
        totalScore: 72,
        weightedScore: 68,
        problemStatement: "Excel-based forecasting is error-prone and lacks AI insights",
        expectedOutcome: "Improve forecast accuracy by 30% and identify new revenue opportunities",
        dataReadiness: "Medium - ERP data needs integration",
        businessImpact: "Increase revenue planning accuracy by 30%",
        feasibility: "Medium - Data integration required",
        risks: ["Data quality issues", "Change resistance from finance team"],
      },
      {
        id: 3,
        name: "Automated Inventory Optimization",
        department: "Operations",
        totalScore: 68,
        weightedScore: 65,
        problemStatement: "Manual inventory management leads to stockouts and excess inventory",
        expectedOutcome: "Reduce stockouts by 80% and optimize inventory levels by 20%",
        dataReadiness: "Medium - IoT sensor data integration needed",
        businessImpact: "Reduce inventory carrying costs by 15%",
        feasibility: "Medium - IoT integration complexity",
        risks: ["Hardware deployment costs", "Sensor data accuracy"],
      },
    ];
    setFormData((prev) => ({ ...prev, useCases: sampleUseCases }));
  };

  const getStatusColor = (score) => {
    if (score >= 80) return "bg-green-100 text-green-700";
    if (score >= 60) return "bg-blue-100 text-blue-700";
    if (score >= 40) return "bg-amber-100 text-amber-700";
    return "bg-red-100 text-red-700";
  };

  const rankedUseCases = [...formData.useCases].sort((a, b) => b.weightedScore - a.weightedScore);

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
              tab.id === "use-case-shortlisting-report-level1"
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
              Use Case Shortlisting Report
            </h3>
            <p className="text-xs text-on-surface-variant mt-1">
              Summary of evaluated use cases with recommendations for next-level development.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50/50 rounded-xl p-4">
              <h4 className="font-label-md text-[11px] uppercase tracking-wider text-blue-600 mb-2">
                Total Evaluated
              </h4>
              <p className="text-2xl font-bold text-on-surface">
                {formData.useCases.length}
              </p>
              <p className="text-xs text-on-surface-variant mt-1">
                Use cases evaluated at Level 1
              </p>
            </div>

            <div className="bg-green-50/50 rounded-xl p-4">
              <h4 className="font-label-md text-[11px] uppercase tracking-wider text-green-600 mb-2">
                Shortlisted
              </h4>
              <p className="text-2xl font-bold text-on-surface">
                {rankedUseCases.filter((uc) => uc.weightedScore >= 70).length}
              </p>
              <p className="text-xs text-on-surface-variant mt-1">
                Ready for Level 2 development
              </p>
            </div>

            <div className="bg-amber-50/50 rounded-xl p-4">
              <h4 className="font-label-md text-[11px] uppercase tracking-wider text-amber-600 mb-2">
                Business Priority
              </h4>
              <p className="text-sm font-bold text-on-surface">
                {formData.businessPriority}
              </p>
              <p className="text-xs text-on-surface-variant mt-1">
                Current business priority level
              </p>
            </div>
          </div>

          <div className="bg-surface-container/30 rounded-xl p-5">
            <h4 className="font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-3">
              Scoring Summary Table
            </h4>
            <div className="grid grid-cols-6 gap-3 text-[10px] font-medium text-on-surface-variant border-b border-outline-variant/20 pb-2">
              <div>Rank</div>
              <div>Use Case Name</div>
              <div>Department</div>
              <div>Total Score</div>
              <div>Weighted Score</div>
              <div>Status</div>
            </div>
            <div className="space-y-2 mt-2">
              {rankedUseCases.map((useCase, index) => (
                <div
                  key={useCase.id}
                  className="grid grid-cols-6 gap-3 text-[11px] text-on-surface items-center hover:bg-surface-container/20 p-2 rounded-lg transition-colors"
                >
                  <div className="font-bold text-on-surface-variant">
                    #{index + 1}
                  </div>
                  <div className="font-medium">
                    {useCase.name}
                  </div>
                  <div>
                    <span className="inline-flex px-2 py-1 rounded-full text-[10px] font-medium bg-blue-50 text-blue-700">
                      {useCase.department}
                    </span>
                  </div>
                  <div>
                    <span className={`inline-flex px-2 py-1 rounded-full text-[10px] font-bold ${getStatusColor(useCase.totalScore)}`}>
                      {useCase.totalScore}
                    </span>
                  </div>
                  <div>
                    <span className={`inline-flex px-2 py-1 rounded-full text-[10px] font-bold ${getStatusColor(useCase.weightedScore)}`}>
                      {useCase.weightedScore}
                    </span>
                  </div>
                  <div>
                    {useCase.weightedScore >= 80 ? (
                      <span className="inline-flex px-2 py-1 rounded-full text-[10px] font-bold bg-green-100 text-green-700">
                        Proceed
                      </span>
                    ) : useCase.weightedScore >= 60 ? (
                      <span className="inline-flex px-2 py-1 rounded-full text-[10px] font-bold bg-blue-100 text-blue-700">
                        Defer
                      </span>
                    ) : (
                      <span className="inline-flex px-2 py-1 rounded-full text-[10px] font-bold bg-amber-100 text-amber-700">
                        Re-evaluate
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-3">
              Final Shortlisted Use Cases
            </h4>
            <div className="space-y-4">
              {rankedUseCases.filter((uc) => uc.weightedScore >= 70).map((useCase) => (
                <div
                  key={useCase.id}
                  className="bg-green-50/30 rounded-xl p-5 border border-green-200/50"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h5 className="font-medium text-on-surface">
                        {useCase.name}
                      </h5>
                      <p className="text-[10px] text-on-surface-variant mt-1">
                        Department: {useCase.department}
                      </p>
                    </div>
                    <span className="inline-flex px-3 py-1 rounded-full text-[10px] font-bold bg-green-100 text-green-700">
                      Proceed to Level 2
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-[10px] font-semibold text-on-surface-variant uppercase tracking-wider mb-1">
                        Problem Statement
                      </p>
                      <p className="text-[11px] text-on-surface">
                        {useCase.problemStatement}
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] font-semibold text-on-surface-variant uppercase tracking-wider mb-1">
                        Expected Outcome
                      </p>
                      <p className="text-[11px] text-on-surface">
                        {useCase.expectedOutcome}
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] font-semibold text-on-surface-variant uppercase tracking-wider mb-1">
                        Data Readiness
                      </p>
                      <p className="text-[11px] text-green-700">
                        {useCase.dataReadiness}
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] font-semibold text-on-surface-variant uppercase tracking-wider mb-1">
                        Business Impact
                      </p>
                      <p className="text-[11px] text-on-surface">
                        {useCase.businessImpact}
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] font-semibold text-on-surface-variant uppercase tracking-wider mb-1">
                        Feasibility
                      </p>
                      <p className="text-[11px] text-blue-700">
                        {useCase.feasibility}
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] font-semibold text-on-surface-variant uppercase tracking-wider mb-1">
                        Dependencies
                      </p>
                      <p className="text-[11px] text-on-surface-variant">
                        {useCase.risks.join(", ")}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
              {rankedUseCases.filter((uc) => uc.weightedScore >= 70).length === 0 && (
                <div className="text-center py-8">
                  <p className="text-on-surface-variant">
                    No use cases meet the Level 2 criteria. All use cases require further evaluation.
                  </p>
                </div>
              )}
            </div>
          </div>

          <div className="bg-blue-50/50 rounded-xl p-5">
            <h4 className="font-label-md text-[11px] uppercase tracking-wider text-blue-600 mb-3">
              Rationale for Selection
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="flex items-start gap-2">
                  <span className="material-symbols-outlined text-green-600 text-[16px] mt-0.5">
                    trending_up
                  </span>
                  <div>
                    <p className="text-[11px] font-semibold text-on-surface">
                      High Business Impact
                    </p>
                    <p className="text-[10px] text-on-surface-variant">
                      Use cases with clear, measurable business outcomes and high ROI potential
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-2">
                  <span className="material-symbols-outlined text-blue-600 text-[16px] mt-0.5">
                    database
                  </span>
                  <div>
                    <p className="text-[11px] font-semibold text-on-surface">
                      Strong Data Availability
                    </p>
                    <p className="text-[10px] text-on-surface-variant">
                      Well-defined data sources with good accessibility and quality
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-2">
                  <span className="material-symbols-outlined text-purple-600 text-[16px] mt-0.5">
                    star
                  </span>
                  <div>
                    <p className="text-[11px] font-semibold text-on-surface">
                      High Management Priority
                    </p>
                    <p className="text-[10px] text-on-surface-variant">
                      Alignment with strategic business objectives
                    </p>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-start gap-2">
                  <span className="material-symbols-outlined text-amber-600 text-[16px] mt-0.5">
                    device_hub
                  </span>
                  <div>
                    <p className="text-[11px] font-semibold text-on-surface">
                      Low Third-Party Dependency
                    </p>
                    <p className="text-[10px] text-on-surface-variant">
                      Minimal external tools or licensing constraints
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-2">
                  <span className="material-symbols-outlined text-red-600 text-[16px] mt-0.5">
                    schedule
                  </span>
                  <div>
                    <p className="text-[11px] font-semibold text-on-surface">
                      Quick Time to Value
                    </p>
                    <p className="text-[10px] text-on-surface-variant">
                      Faster implementation cycles and earlier ROI realization
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-2">
                  <span className="material-symbols-outlined text-indigo-600 text-[16px] mt-0.5">
                    target
                  </span>
                  <div>
                    <p className="text-[11px] font-semibold text-on-surface">
                      Strategic Alignment
                    </p>
                    <p className="text-[10px] text-on-surface-variant">
                      Strong fit with organizational strategy and goals
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-amber-50/50 rounded-xl p-5">
            <h4 className="font-label-md text-[11px] uppercase tracking-wider text-amber-600 mb-3">
              Risks & Mitigations
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider mb-2">
                  Identified Risks
                </p>
                <ul className="text-[10px] text-on-surface space-y-1">
                  <li>• Resource constraints may impact timeline and quality</li>
                  <li>• Technology integration complexity</li>
                  <li>• Change management challenges</li>
                  <li>• Data privacy and security concerns</li>
                </ul>
              </div>
              <div>
                <p className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider mb-2">
                  Mitigation Strategies
                </p>
                <ul className="text-[10px] text-on-surface space-y-1">
                  <li>• Phased implementation with pilot testing</li>
                  <li>• Established governance framework</li>
                  <li>• Comprehensive training programs</li>
                  <li>• Regular security audits and compliance checks</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-surface-container/30 rounded-xl p-5">
            <h4 className="font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-3">
              Recommendations & Next Steps
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider mb-2">
                  Move to Level 2
                </p>
                <ul className="text-[10px] text-on-surface space-y-1">
                  <li>• Assign product owner for shortlisted use cases</li>
                  <li>• Begin BRD/FRD development for approved use cases</li>
                  <li>• Initiate architecture planning and design</li>
                  <li>• Start effort estimation and resource planning</li>
                </ul>
              </div>
              <div>
                <p className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider mb-2">
                  Continuous Improvement
                </p>
                <ul className="text-[10px] text-on-surface space-y-1">
                  <li>• Regular review and re-evaluation of deferred use cases</li>
                  <li>• Monitor emerging technologies and opportunities</li>
                  <li>• Capture lessons learned and best practices</li>
                  <li>• Expand evaluation criteria as organization matures</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-surface-container/30 rounded-xl p-4">
            <h4 className="font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-3">
              Approval Sign-Off
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-[10px] font-semibold text-on-surface-variant mb-1.5">
                  Project Sponsor
                </label>
                <div className="h-8 bg-white rounded border border-outline-variant/30 flex items-center px-2 text-[10px] text-on-surface-variant">
                  Signature & Date
                </div>
              </div>
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
                  AI Lead
                </label>
                <div className="h-8 bg-white rounded border border-outline-variant/30 flex items-center px-2 text-[10px] text-on-surface-variant">
                  Signature & Date
                </div>
              </div>
              <div>
                <label className="block text-[10px] font-semibold text-on-surface-variant mb-1.5">
                  Compliance Officer
                </label>
                <div className="h-8 bg-white rounded border border-outline-variant/30 flex items-center px-2 text-[10px] text-on-surface-variant">
                  Signature & Date
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

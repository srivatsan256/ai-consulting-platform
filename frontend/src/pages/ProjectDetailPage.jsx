import React, { useState, useEffect, useRef } from "react";
import { projectService, documentService, verificationService, chatService, deliverableService } from "../services/api";
import { LEVEL_MODULES, EXECUTIVE_SUMMARY_DOCS, DOC_TYPE_OPTIONS } from "../constants/levelModules";
import TopHeader from "../components/TopHeader";
import "./ProjectDetailPage.css";

const STATUS_COLORS = {
  DISCOVERY: "bg-blue-100 text-blue-700",
  VERIFICATION: "bg-amber-100 text-amber-700",
  PROCESSING: "bg-purple-100 text-purple-700",
  REVIEW: "bg-indigo-100 text-indigo-700",
  COMPLETED: "bg-emerald-100 text-emerald-700",
};

const TABS = [
  { id: "overview", label: "Overview", icon: "info" },
  { id: "verification", label: "Verification", icon: "verified_user" },
  { id: "chat", label: "AI Chat", icon: "smart_toy" },
  { id: "deliverables", label: "Deliverables", icon: "assignment_turned_in" },
];

function getRecommendedDocType(level) {
  const map = {
    1: "USE-CASES",
    2: "PERSONAS",
    3: "BRD",
    4: "EFFORT-EST",
    5: "HLA",
    6: "AI-SECURITY",
    7: "METRICS",
    8: "DEPLOY-GUIDE",
    9: "GOVERNANCE",
    10: "TEST-STRATEGY",
  };
  return map[level] || "OTHER";
}

function getDocTypeLabel(value) {
  return DOC_TYPE_OPTIONS.find((opt) => opt.value === value)?.label || value;
}

export default function ProjectDetailPage({ projectId, onBack }) {
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [uploading, setUploading] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [useAiVerify, setUseAiVerify] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [selectedDocType, setSelectedDocType] = useState("OTHER");
  const [verificationResult, setVerificationResult] = useState(null);
  const [levelModules, setLevelModules] = useState([]);
  const [levelModulesLoading, setLevelModulesLoading] = useState(true);
  const [expandedLevel, setExpandedLevel] = useState(null);
  const chatEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const projectDocs = project?.documents || [];
  const currentLevel = Math.max(1, project?.current_level || 1);
  const recommendedDocType = getRecommendedDocType(currentLevel);
  const currentLevelDocs = projectDocs.filter((doc) => (doc.level || currentLevel) === currentLevel);
  const verifiedCurrentLevelDocs = currentLevelDocs.filter((doc) => doc.verification_status);
  const pendingCurrentLevelDocs = currentLevelDocs.filter((doc) => !doc.verification_status);
  const verificationProgress = currentLevelDocs.length
    ? Math.round((verifiedCurrentLevelDocs.length / currentLevelDocs.length) * 100)
    : 0;
  const verificationUnlocked = currentLevelDocs.length > 0;
  const verificationLocked = !verificationUnlocked;
  const readinessLabel = project?.readiness_score != null ? `${Math.round(project.readiness_score)}%` : "N/A";
  const docById = Object.fromEntries(projectDocs.map((doc) => [doc.id, doc]));

  const openDocument = (documentId) => {
    const doc = docById[documentId];
    if (doc?.file_url) {
      window.open(doc.file_url, "_blank", "noopener,noreferrer");
    }
  };

  useEffect(() => {
    if (projectId) fetchProject();
    setLevelModules(LEVEL_MODULES);
    setLevelModulesLoading(false);
  }, [projectId]);

  useEffect(() => {
    setSelectedDocType(getRecommendedDocType(currentLevel));
  }, [currentLevel]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

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

  const handleUpload = async (files) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    try {
      for (const file of files) {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("doc_type", selectedDocType);
        formData.append("level", String(Math.max(1, project?.current_level || 1)));
        const res = await documentService.upload(projectId, formData);
        setVerificationResult(res.data?.verification || null);
      }
      fetchProject();
    } catch (err) {
      console.error("Upload failed:", err);
    } finally {
      setUploading(false);
    }
  };

  const handleVerify = async () => {
    setVerifying(true);
    setVerificationResult(null);
    try {
      const res = await verificationService.verifyAll(projectId, useAiVerify);
      setVerificationResult(res.data);
      fetchProject();
    } catch (err) {
      console.error("Verification failed:", err);
    } finally {
      setVerifying(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await deliverableService.generate(projectId);
      if (res.data.zip_download_url) {
        window.open(res.data.zip_download_url, "_blank");
      }
      fetchProject();
    } catch (err) {
      console.error("Generation failed:", err);
    } finally {
      setGenerating(false);
    }
  };

  const handleChat = async () => {
    if (!chatInput.trim() || !projectId) return;
    const q = chatInput.trim();
    setChatInput("");
    setChatMessages((prev) => [...prev, { role: "user", content: q }]);
    setChatLoading(true);
    try {
      const res = await chatService.ask(projectId, q);
      setChatMessages((prev) => [...prev, { role: "assistant", content: res.data.answer }]);
    } catch (err) {
      setChatMessages((prev) => [...prev, { role: "assistant", content: "Sorry, I could not process that question. Please ensure the backend is running." }]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleUpload(Array.from(e.dataTransfer.files));
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / 1048576).toFixed(1) + " MB";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="text-center py-20">
        <span className="material-symbols-outlined text-[48px] text-outline-variant">error</span>
        <p className="text-on-surface-variant mt-3">Project not found</p>
        <button onClick={onBack} className="pdetail-notfound-btn">Go Back</button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <TopHeader
        title={project.project_name}
        subtitle={project.company_name}
        actions={
          <button onClick={onBack} className="pdetail-back-btn">
            <span className="material-symbols-outlined text-[18px]">arrow_back</span>
            Back
          </button>
        }
      />

      {/* Status Bar */}
      <div className="pdetail-statusbar soft-shadow">
        <span className={`pdetail-badge ${STATUS_COLORS[project.status] || "bg-gray-100 text-gray-600"}`}>
          {project.status}
        </span>
        {project.readiness_score != null && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-on-surface-variant">Readiness:</span>
            <div className="pdetail-progress">
              <div className="h-full bg-primary rounded-full" style={{ width: `${project.readiness_score}%` }} />
            </div>
            <span className="text-xs font-bold text-on-surface">{project.readiness_score}%</span>
          </div>
        )}
        <span className="pdetail-meta">
          <span className="material-symbols-outlined text-[14px]">numbers</span>
          Current Level L{Math.max(1, project.current_level || 1)}
        </span>
        {project.expected_timeline && (
          <span className="pdetail-meta">
            <span className="material-symbols-outlined text-[14px]">schedule</span>
            {project.expected_timeline}
          </span>
        )}
        <span className="pdetail-meta">
          <span className="material-symbols-outlined text-[14px]">description</span>
          {projectDocs.length} documents
        </span>
        <div className="flex items-center gap-2 ml-auto">
          <div className="pdetail-stat-chip">
            <span className="material-symbols-outlined text-[14px] text-primary">layers</span>
            {project.completed_levels?.length || 0} levels complete
          </div>
          <div className="pdetail-stat-chip">
            <span className="material-symbols-outlined text-[14px] text-primary">verified_user</span>
            Readiness {readinessLabel}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="pdetail-tabs soft-shadow">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`pdetail-tab ${
              activeTab === tab.id
                ? "pdetail-tab-active"
                : tab.id === "verification" && verificationLocked
                  ? "pdetail-tab-locked"
                  : "pdetail-tab-idle"
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">{tab.icon}</span>
            {tab.id === "verification" && (
              <span className={`pdetail-tab-badge ${verificationLocked ? "bg-amber-100 text-amber-700" : "bg-emerald-100 text-emerald-700"}`}>
                {verificationLocked ? "Locked" : "Unlocked"}
              </span>
            )}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="pdetail-panel soft-shadow">
        {activeTab === "overview" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="pdetail-section-label">Company</h4>
                <p className="text-on-surface text-sm">{project.company_name}</p>
              </div>
              <div>
                <h4 className="pdetail-section-label">Industry</h4>
                <p className="text-on-surface text-sm">{project.industry || "Not specified"}</p>
              </div>
              <div>
                <h4 className="pdetail-section-label">Team Members</h4>
                <p className="text-on-surface text-sm">{project.team_members || "Not specified"}</p>
              </div>
              <div>
                <h4 className="pdetail-section-label">Timeline</h4>
                <p className="text-on-surface text-sm">{project.expected_timeline || "Not specified"}</p>
              </div>
            </div>
            {project.objectives && (
              <div>
                <h4 className="pdetail-section-label">Objectives</h4>
                <p className="text-on-surface text-sm leading-relaxed">{project.objectives}</p>
              </div>
            )}

            {/* Level-by-Level Module Table */}
            <div className="mt-8">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="pdetail-h3">Level-by-Level Module Conditions</h3>
                  <p className="text-xs text-on-surface-variant mt-1">Each level must meet its conditions before the next level unlocks</p>
                </div>
                <div className="flex items-center gap-3 text-[11px]">
                  <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Completed</span>
                  <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-primary" /> Current</span>
                  <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-outline-variant/40" /> Locked</span>
                </div>
              </div>

              <div className="pdetail-table-wrap">
                {levelModulesLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="w-6 h-6 border-4 border-primary border-t-transparent rounded-full animate-spin" />
                  </div>
                ) : levelModules.length === 0 ? (
                  <div className="text-center py-12">
                    <span className="material-symbols-outlined text-[40px] text-outline-variant">table_chart</span>
                    <p className="text-on-surface-variant mt-2 text-sm">No level modules configured. Run seed_level_modules to populate.</p>
                  </div>
                ) : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="pdetail-table-head-row">
                      <th className="pdetail-th w-[180px]">Level</th>
                      <th className="pdetail-th min-w-[250px]">Must Include</th>
                      <th className="pdetail-th min-w-[220px]">Recommended</th>
                      <th className="pdetail-th text-center w-[100px]">Status</th>
                      <th className="pdetail-th w-[200px]">Condition</th>
                    </tr>
                  </thead>
                  <tbody>
                    {levelModules.map((mod) => {
                      const isCompleted = project.completed_levels?.includes(mod.level);
                      const isCurrent = currentLevel === mod.level;
                      const isLocked = !isCompleted && !isCurrent;
                      const isExpanded = expandedLevel === mod.level;

                      return (
                        <React.Fragment key={mod.level}>
                          <tr
                            className={`pdetail-row ${
                              isCurrent ? "bg-primary/5" : isCompleted ? "bg-emerald-50/30" : "hover:bg-surface-container-low/50"
                            }`}
                            onClick={() => setExpandedLevel(isExpanded ? null : mod.level)}
                          >
                            <td className="pdetail-td">
                              <div className="flex items-center gap-3">
                                <div className={`pdetail-level-icon ${
                                  isCompleted ? "bg-emerald-100" : isCurrent ? "bg-primary/10" : "bg-surface-container"
                                }`}>
                                  {isCompleted ? (
                                    <span className="material-symbols-outlined text-emerald-600 text-[18px]" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                                  ) : isCurrent ? (
                                    <span className="material-symbols-outlined text-primary text-[18px]">{mod.icon}</span>
                                  ) : (
                                    <span className="material-symbols-outlined text-outline-variant text-[18px]">lock</span>
                                  )}
                                </div>
                                <div className="min-w-0">
                                  <p className={`pdetail-level-title ${isCurrent ? "text-primary" : isCompleted ? "text-emerald-700" : "text-on-surface-variant"}`}>
                                    Level {mod.level} · {mod.title}
                                  </p>
                                  <p className="text-[11px] text-on-surface-variant/70 truncate mt-0.5 max-w-[140px]">{mod.description?.slice(0, 60)}...</p>
                                </div>
                              </div>
                            </td>
                            <td className="pdetail-td">
                              <ul className="space-y-1">
                                {(mod.must_include || []).slice(0, 3).map((item, i) => (
                                  <li key={item.id || i} className="pdetail-list-item">
                                    <span className="material-symbols-outlined text-amber-500 text-[12px] mt-0.5 shrink-0">flag</span>
                                    <span className="leading-tight">{item.text || item}</span>
                                  </li>
                                ))}
                                {(mod.must_include || []).length > 3 && (
                                  <li className="text-[10px] text-on-surface-variant/60 pl-4">+{mod.must_include.length - 3} more</li>
                                )}
                              </ul>
                            </td>
                            <td className="pdetail-td">
                              <ul className="space-y-1">
                                {(mod.recommended || []).slice(0, 2).map((item, i) => (
                                  <li key={item.id || i} className="pdetail-list-item-soft">
                                    <span className="material-symbols-outlined text-blue-400 text-[12px] mt-0.5 shrink-0">lightbulb</span>
                                    <span className="leading-tight">{item.text || item}</span>
                                  </li>
                                ))}
                                {(mod.recommended || []).length > 2 && (
                                  <li className="text-[10px] text-on-surface-variant/60 pl-4">+{mod.recommended.length - 2} more</li>
                                )}
                              </ul>
                            </td>
                            <td className="pdetail-td text-center">
                              <span className={`pdetail-pill ${
                                isCompleted ? "bg-emerald-100 text-emerald-700" : isCurrent ? "bg-primary/10 text-primary" : "bg-surface-container text-on-surface-variant/50"
                              }`}>
                                {isCompleted ? "PASSED" : isCurrent ? "ACTIVE" : "LOCKED"}
                              </span>
                            </td>
                            <td className="pdetail-td">
                              <p className="text-[11px] text-on-surface-variant leading-tight">
                                {isCompleted
                                  ? "All required items verified. Level passed."
                                  : isCurrent
                                    ? `Upload ${mod.required_documents.length} document(s) and meet ${mod.required_count} required conditions.`
                                    : "Complete previous level to unlock."}
                              </p>
                            </td>
                          </tr>
                          {isExpanded && (
                            <tr className="pdetail-expanded-row">
                              <td colSpan={6} className="px-4 py-4">
                                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                                  <div>
                                    <p className="pdetail-detail-label">Description</p>
                                    <p className="text-xs text-on-surface leading-relaxed">{mod.description}</p>
                                  </div>
                                  <div>
                                    <p className="pdetail-detail-label-amber">All Must Include ({(mod.must_include || []).length})</p>
                                    <ul className="space-y-1.5">
                                      {(mod.must_include || []).map((item, i) => (
                                        <li key={item.id || i} className="pdetail-list-item">
                                          <span className="material-symbols-outlined text-amber-500 text-[12px] mt-0.5 shrink-0">flag</span>
                                          {item.text || item}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                  <div>
                                    <p className="pdetail-detail-label-blue">All Recommended ({(mod.recommended || []).length})</p>
                                    <ul className="space-y-1.5">
                                      {(mod.recommended || []).map((item, i) => (
                                        <li key={item.id || i} className="pdetail-list-item-soft">
                                          <span className="material-symbols-outlined text-blue-400 text-[12px] mt-0.5 shrink-0">lightbulb</span>
                                          {item.text || item}
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                </div>
                                <div className="mt-4">
                                  <p className="pdetail-detail-label">Required Documents</p>
                                  <div className="flex flex-wrap gap-2">
                                    {(mod.required_documents || []).map((doc, i) => (
                                      <span key={doc.id || i} className="pdetail-doc-chip">
                                        {doc.label}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      );
                    })}
                  </tbody>
                </table>
                )}
              </div>
            </div>

            {/* Executive Summary - Mandatory Core Documents */}
            <div className="mt-8">
              <h3 className="pdetail-h3">Executive Summary - Mandatory Core Documents</h3>
              <p className="text-xs text-on-surface-variant mt-1">Minimum essential documents every AI project must have across all levels</p>
              <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {EXECUTIVE_SUMMARY_DOCS.map((doc) => (
                  <div key={doc} className="pdetail-exec-card">
                    <span className="material-symbols-outlined text-primary text-[18px]">task_alt</span>
                    <span className="text-xs font-medium text-on-surface">{doc}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === "verification" && (
          <div className="space-y-4">
            {verificationResult && (
              <div className={`rounded-xl border p-4 text-sm ${verificationResult.level_status === "PASSED" ? "border-emerald-200 bg-emerald-50 text-emerald-800" : "border-amber-200 bg-amber-50 text-amber-800"}`}>
                Level {verificationResult.level} {verificationResult.level_status}. Unlock next level: {verificationResult.unlock_next_level ? "true" : "false"}.
              </div>
            )}

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              <div className="pdetail-stat-card">
                <p className="pdetail-stat-label">Current Level</p>
                <p className="pdetail-stat-value">L{currentLevel}</p>
                <p className="pdetail-stat-sub">Unlocked workspace</p>
              </div>
              <div className="pdetail-stat-card">
                <p className="pdetail-stat-label">Docs in Level</p>
                <p className="pdetail-stat-value">{currentLevelDocs.length}</p>
                <p className="pdetail-stat-sub">{verifiedCurrentLevelDocs.length} verified</p>
              </div>
              <div className="pdetail-stat-card">
                <p className="pdetail-stat-label">Verification</p>
                <p className="pdetail-stat-value">{verificationProgress}%</p>
                <div className="pdetail-bar-track">
                  <div className="h-full rounded-full bg-primary" style={{ width: `${verificationProgress}%` }} />
                </div>
              </div>
              <div className="pdetail-stat-card">
                <p className="pdetail-stat-label">Next Step</p>
                <p className="pdetail-stat-value">{verificationUnlocked ? "Verify" : "Upload"}</p>
                <p className="pdetail-stat-sub">{verificationUnlocked ? "Run current level checks" : "Add current level documents"}</p>
              </div>
            </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="pdetail-upload-panel">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <h4 className="pdetail-h4">Upload Documents</h4>
                    <p className="text-xs text-on-surface-variant mt-1">Current level: L{currentLevel}</p>
                  </div>
                  <div className="pdetail-doctype-badge">
                    <span className="material-symbols-outlined text-[16px]">flag</span>
                    {getDocTypeLabel(recommendedDocType)}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="pdetail-info-card">
                    <p className="pdetail-stat-label">Suggested file type</p>
                    <p className="pdetail-info-value">{getDocTypeLabel(recommendedDocType)}</p>
                  </div>
                  <div className="pdetail-info-card">
                    <p className="pdetail-stat-label">Current focus</p>
                    <p className="pdetail-info-value">{verificationUnlocked ? "Ready for review" : "Waiting for upload"}</p>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2">
                  {["Level docs", "PDF/OCR", "Semantic match", "Page-by-page"].map((chip) => (
                    <span key={chip} className="pdetail-chip">
                      {chip}
                    </span>
                  ))}
                </div>

                <div
                  onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={`pdetail-dropzone ${
                    dragOver ? "border-primary bg-primary/5" : "border-outline-variant/40 hover:border-primary/50"
                  }`}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".pdf,.docx,.xlsx,.doc,.txt"
                    onChange={(e) => handleUpload(Array.from(e.target.files))}
                    className="hidden"
                  />
                  <span className="material-symbols-outlined text-[40px] text-outline-variant">cloud_upload</span>
                  <p className="text-on-surface-variant text-sm mt-2">
                    {uploading ? "Uploading..." : "Drag & drop files here or click to browse"}
                  </p>
                  <p className="text-outline text-xs mt-1">PDF, DOCX, XLSX, TXT</p>
                </div>

                {project.documents && project.documents.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="pdetail-h4">Uploaded Documents</h4>
                    {project.documents.map((doc) => (
                      <div key={doc.id} className="pdetail-doc-row">
                        <span className="material-symbols-outlined text-primary text-[20px]">description</span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-on-surface truncate">{doc.file?.split("/").pop() || doc.doc_type}</p>
                          <p className="text-xs text-on-surface-variant">{getDocTypeLabel(doc.doc_type)} · Uploaded {new Date(doc.uploaded_at).toLocaleDateString()}</p>
                        </div>
                        <button
                          onClick={() => openDocument(doc.id)}
                          disabled={!doc.file_url}
                          className="pdetail-open-btn"
                        >
                          Open PDF
                        </button>
                        <span className={`pdetail-mini-badge ${
                          doc.verification_status ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"
                        }`}>
                          {doc.verification_status ? "Passed" : "Pending"}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="space-y-4">
                {!verificationUnlocked && (
                  <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800 flex items-start gap-3">
                    <span className="material-symbols-outlined text-[20px] mt-0.5">lock</span>
                    <div>
                      <p className="font-semibold">Verification locked</p>
                      <p className="text-amber-700 mt-1">Upload documents for Level {currentLevel} to unlock this tab.</p>
                    </div>
                  </div>
                )}
                {verificationUnlocked && (
                  <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800 flex items-start gap-3">
                    <span className="material-symbols-outlined text-[20px] mt-0.5">lock_open</span>
                    <div>
                      <p className="font-semibold">Verification unlocked</p>
                      <p className="text-emerald-700 mt-1">Current level documents are ready for verification.</p>
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <h4 className="pdetail-h4">Document Verification</h4>
                  <div className="flex items-center gap-3">
                    <label className="pdetail-check-label">
                      <input
                        type="checkbox"
                        checked={useAiVerify}
                        onChange={(e) => setUseAiVerify(e.target.checked)}
                        disabled={!verificationUnlocked}
                        className="pdetail-checkbox"
                      />
                      Use AI Analysis
                    </label>
                    <button
                      onClick={handleVerify}
                      disabled={verifying || !verificationUnlocked}
                      className="pdetail-primary-btn"
                    >
                      {verifying ? (
                        <div className="w-4 h-4 border-2 border-on-primary border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <span className="material-symbols-outlined text-[16px]">verified_user</span>
                      )}
                      {verifying ? "Verifying..." : "Run Verification"}
                    </button>
                  </div>
                </div>

                {!verificationUnlocked && !project.documents?.length && (
                  <div className="text-center py-12">
                    <span className="material-symbols-outlined text-[48px] text-outline-variant">upload_file</span>
                    <p className="text-on-surface-variant mt-3 text-sm">Upload documents first to run verification</p>
                  </div>
                )}

                {verificationResult && (
                  <div className="space-y-3">
                    <div className="pdetail-result-card">
                      <div className="flex items-center gap-3">
                        <span className="material-symbols-outlined text-primary text-[24px]">analytics</span>
                        <div>
                          <p className="text-sm font-bold text-on-surface">Readiness Score: {verificationResult.readiness_score}%</p>
                          <p className="text-xs text-on-surface-variant">Status: {verificationResult.status}</p>
                        </div>
                      </div>
                    </div>
                    {verificationResult.results?.map((result, idx) => (
                      <div key={idx} className="pdetail-result-item">
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`w-2 h-2 rounded-full ${result.passed ? "bg-emerald-500" : "bg-red-500"}`} />
                          <span className="text-sm font-semibold text-on-surface">{result.doc_type} Document</span>
                          <span className="text-xs text-on-surface-variant ml-auto">Score: {result.score}%</span>
                        </div>
                        <div className="flex flex-wrap gap-2 text-[11px] text-on-surface-variant mb-3">
                          <span className="pdetail-meta-pill">{result.page_number ? `Page ${result.page_number}` : "Page N/A"}</span>
                          <span className="pdetail-meta-pill">{result.match_method || "no match method"}</span>
                          <span className="pdetail-meta-pill">Confidence {result.confidence != null ? `${Math.round(result.confidence * 100)}%` : "N/A"}</span>
                          {result.ocr_used && <span className="pdetail-meta-pill">OCR</span>}
                        </div>
                        {result.evidence && (
                          <p className="text-xs text-on-surface-variant p-3 rounded-lg bg-surface-container-low mb-3 leading-relaxed">
                            {result.evidence}
                          </p>
                        )}
                        {result.coordinates && (
                          <p className="text-[11px] text-on-surface-variant mb-2">
                            Coordinates: {Array.isArray(result.coordinates) ? result.coordinates.map((n) => Math.round(n)).join(", ") : "N/A"}
                          </p>
                        )}
                        {result.missing_keywords?.length > 0 && (
                          <p className="text-xs text-red-600 mt-1">Missing keywords: {result.missing_keywords.join(", ")}</p>
                        )}
                        {result.missing_sections?.length > 0 && (
                          <p className="text-xs text-amber-600 mt-1">Missing sections: {result.missing_sections.join(", ")}</p>
                        )}
                        <button
                          onClick={() => openDocument(result.document_id)}
                          disabled={!docById[result.document_id]?.file_url}
                          className="pdetail-outline-btn"
                        >
                          Review Source PDF
                        </button>
                        {result.ai_feedback && (
                          <p className="text-xs text-on-surface-variant mt-2 p-2 bg-surface-container rounded-lg">{result.ai_feedback}</p>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {!verificationResult && project.readiness_score != null && (
                  <div className="pdetail-result-card">
                    <p className="text-sm text-on-surface-variant">Previous readiness score: <span className="font-bold text-on-surface">{project.readiness_score}%</span></p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === "chat" && (
          <div className="flex flex-col h-[500px]">
            <div className="pdetail-chat-list">
              {chatMessages.length === 0 && (
                <div className="text-center py-12">
                  <span className="material-symbols-outlined text-[48px] text-outline-variant">smart_toy</span>
                  <p className="text-on-surface-variant mt-3 text-sm">Ask questions about this project's documents</p>
                  <div className="flex flex-wrap gap-2 justify-center mt-4">
                    {["What are the main requirements?", "Summarize the business objectives", "What risks are identified?"].map((q) => (
                      <button
                        key={q}
                        onClick={() => { setChatInput(q); }}
                        className="pdetail-suggestion"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              {chatMessages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`pdetail-msg-bubble ${
                    msg.role === "user"
                      ? "pdetail-msg-user"
                      : "pdetail-msg-assistant"
                  }`}>
                    {msg.content}
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="pdetail-typing-bubble">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-outline-variant rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                      <div className="w-2 h-2 bg-outline-variant rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                      <div className="w-2 h-2 bg-outline-variant rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
            <div className="flex gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleChat()}
                placeholder="Ask about project documents..."
                className="pdetail-chat-input"
              />
              <button
                onClick={handleChat}
                disabled={!chatInput.trim() || chatLoading}
                className="pdetail-send-btn"
              >
                <span className="material-symbols-outlined text-[18px]">send</span>
              </button>
            </div>
          </div>
        )}

        {activeTab === "deliverables" && (
          <div className="space-y-6">
            <div className="text-center py-8">
              <span className="material-symbols-outlined text-[48px] text-primary">assignment_turned_in</span>
              <h4 className="font-semibold text-on-surface mt-3">Generate Project Deliverables</h4>
              <p className="text-on-surface-variant text-sm mt-1 max-w-md mx-auto">
                Generate BRD, FRD, PRD, verification summary, project timeline, and metadata as a ZIP package.
              </p>
              <button
                onClick={handleGenerate}
                disabled={generating}
                className="pdetail-generate-btn"
              >
                {generating ? (
                  <div className="w-4 h-4 border-2 border-on-primary border-t-transparent rounded-full animate-spin" />
                ) : (
                  <span className="material-symbols-outlined text-[18px]">auto_awesome</span>
                )}
                {generating ? "Generating..." : "Generate Deliverables"}
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { icon: "description", title: "BRD", desc: "Business Requirements Document" },
                { icon: "article", title: "FRD", desc: "Functional Requirements Document" },
                { icon: "newspaper", title: "PRD", desc: "Product Requirements Document" },
              ].map((item) => (
                <div key={item.title} className="pdetail-deliverable-card">
                  <span className="material-symbols-outlined text-primary text-[28px]">{item.icon}</span>
                  <p className="text-sm font-bold text-on-surface mt-2">{item.title}</p>
                  <p className="text-xs text-on-surface-variant">{item.desc}</p>
                </div>
              ))}
            </div>

            {project.status === "COMPLETED" && (
              <div className="pdetail-complete-banner">
                <span className="material-symbols-outlined text-emerald-600 text-[24px]" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>
                <div>
                  <p className="text-sm font-bold text-emerald-800">Deliverables Generated</p>
                  <p className="text-xs text-emerald-600">Project status: {project.status}</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

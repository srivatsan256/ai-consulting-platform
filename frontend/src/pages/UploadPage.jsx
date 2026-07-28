import React, { useState, useEffect, useRef } from "react";
import { projectService, documentService } from "../services/api";
import TopHeader from "../components/TopHeader";

export default function UploadPage({ projectId, onSelectProject }) {
  const [projects, setProjects] = useState([]);
  const [selectedId, setSelectedId] = useState(projectId || "");
  const [selectedProject, setSelectedProject] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(true);
  const fileInputRef = useRef(null);

  const [requiredDocs, setRequiredDocs] = useState([]);
  const [currentDocIndex, setCurrentDocIndex] = useState(0);
  const [uploadStatus, setUploadStatus] = useState({});
  const [showRevisionPrompt, setShowRevisionPrompt] = useState(false);
  const [lastVerificationResult, setLastVerificationResult] = useState(null);
  const [lastMissingKeywords, setLastMissingKeywords] = useState([]);
  const [requiredDocsLoading, setRequiredDocsLoading] = useState(false);

  useEffect(() => { fetchProjects(); }, []);
  useEffect(() => { if (projectId) setSelectedId(projectId); }, [projectId]);
  useEffect(() => {
    setSelectedProject(projects.find((p) => p.id === selectedId) || null);
  }, [projects, selectedId]);
  useEffect(() => {
    if (selectedId) fetchRequiredDocs();
  }, [selectedId]);

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

  const fetchRequiredDocs = async () => {
    setRequiredDocsLoading(true);
    try {
      const res = await projectService.requiredDocStatus(selectedId);
      const docs = res.data.required_docs || [];
      setRequiredDocs(docs);

      const statusMap = {};
      docs.forEach((doc) => {
        if (doc.has_passed) {
          statusMap[doc.doc_type] = "verified";
        } else if (doc.uploaded_count > 0) {
          statusMap[doc.doc_type] = "failed";
        } else {
          statusMap[doc.doc_type] = "pending";
        }
      });
      setUploadStatus(statusMap);

      const firstPendingIndex = docs.findIndex((doc) => !doc.has_passed);
      setCurrentDocIndex(firstPendingIndex >= 0 ? firstPendingIndex : docs.length);
      setShowRevisionPrompt(false);
      setLastVerificationResult(null);
      setLastMissingKeywords([]);
    } catch (err) {
      console.error("Failed to fetch required docs:", err);
    } finally {
      setRequiredDocsLoading(false);
    }
  };

  const currentRequiredDoc = requiredDocs[currentDocIndex];
  const allDocsVerified = requiredDocs.length > 0 && requiredDocs.every((doc) => doc.has_passed);

  const handleUpload = async (files) => {
    if (!selectedId || !files.length || !currentRequiredDoc) return;
    const file = files[0];
    setUploading(true);
    setShowRevisionPrompt(false);
    setLastVerificationResult(null);
    setLastMissingKeywords([]);

    setUploadStatus((prev) => ({ ...prev, [currentRequiredDoc.doc_type]: "uploading" }));

    const formData = new FormData();
    formData.append("file", file);
    formData.append("doc_type", currentRequiredDoc.doc_type);
    formData.append("level", String(Math.max(1, selectedProject?.current_level || 1)));

    try {
      const res = await documentService.upload(selectedId, formData);
      const verification = res.data?.verification;
      const passed = verification?.passed;

      if (passed) {
        setUploadStatus((prev) => ({ ...prev, [currentRequiredDoc.doc_type]: "verified" }));
        setShowRevisionPrompt(false);
        setLastVerificationResult(null);
        setLastMissingKeywords([]);
        if (currentDocIndex < requiredDocs.length - 1) {
          setCurrentDocIndex((prev) => prev + 1);
        }
      } else {
        setUploadStatus((prev) => ({ ...prev, [currentRequiredDoc.doc_type]: "failed" }));
        setShowRevisionPrompt(true);
        setLastVerificationResult(verification);
        setLastMissingKeywords(verification?.missing_requirements || []);
      }
    } catch (err) {
      console.error("Upload failed:", err);
      setUploadStatus((prev) => ({ ...prev, [currentRequiredDoc.doc_type]: "failed" }));
      setShowRevisionPrompt(true);
      setLastVerificationResult(null);
      setLastMissingKeywords([]);
    } finally {
      setUploading(false);
      await fetchProjects();
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files.length > 0) {
      handleUpload([e.dataTransfer.files[0]]);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "verified": return "check_circle";
      case "failed": return "error";
      case "uploading": return "hourglass_top";
      default: return "radio_button_unchecked";
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "verified": return "text-emerald-500";
      case "failed": return "text-red-500";
      case "uploading": return "text-amber-500 animate-pulse";
      default: return "text-outline-variant";
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case "verified": return "Verified";
      case "failed": return "Failed - Revise & Re-upload";
      case "uploading": return "Uploading...";
      default: return "Pending";
    }
  };

  return (
    <div className="space-y-6">
      <TopHeader
        title="Upload Documents"
        subtitle="Document management"
      />

      {/* Project Selector */}
      <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
        <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-2">
          Select Project
        </label>
        <select
          value={selectedId}
          onChange={(e) => setSelectedId(e.target.value)}
          className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
        >
          <option value="">Choose a project</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.project_name} ({p.company_name})</option>
          ))}
        </select>
        {selectedProject && (
          <p className="mt-3 text-xs text-on-surface-variant">
            Current unlocked level: L{Math.max(1, selectedProject.current_level || 1)}
          </p>
        )}
      </div>

      {/* Required Documents Progress */}
      {selectedId && requiredDocs.length > 0 && (
        <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-on-surface text-sm">Required Documents</h3>
            <span className="text-xs text-on-surface-variant">
              {requiredDocs.filter((d) => d.has_passed).length} of {requiredDocs.length} verified
            </span>
          </div>
          <div className="space-y-3">
            {requiredDocs.map((doc, index) => {
              const status = uploadStatus[doc.doc_type] || "pending";
              const isCurrentDoc = index === currentDocIndex;
              return (
                <div
                  key={doc.doc_type}
                  className={`flex items-center gap-3 p-3 rounded-lg transition-colors ${
                    isCurrentDoc
                      ? "bg-primary/5 border border-primary/30"
                      : "bg-surface-container-low"
                  }`}
                >
                  <span className={`material-symbols-outlined text-[20px] ${getStatusColor(status)}`}>
                    {getStatusIcon(status)}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-on-surface">{doc.label}</p>
                    <p className="text-[11px] text-on-surface-variant">{doc.doc_type}</p>
                  </div>
                  <span className={`text-[10px] font-medium ${
                    status === "verified" ? "text-emerald-600" : status === "failed" ? "text-red-600" : "text-on-surface-variant"
                  }`}>
                    {getStatusLabel(status)}
                  </span>
                  {isCurrentDoc && status !== "verified" && (
                    <span className="material-symbols-outlined text-[16px] text-primary animate-pulse">
                      arrow_forward
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Upload Area */}
      {selectedId && currentRequiredDoc && !allDocsVerified && (
        <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
          <div className="mb-4">
            <h3 className="font-semibold text-on-surface text-sm mb-1">
              Upload: {currentRequiredDoc.label}
            </h3>
            <p className="text-xs text-on-surface-variant">
              Document {currentDocIndex + 1} of {requiredDocs.length} - Please upload this document before proceeding to the next one.
            </p>
          </div>
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors cursor-pointer ${
              dragOver ? "border-primary bg-primary/5" : "border-outline-variant/40 hover:border-primary/50"
            }`}
          >
            <input
              type="file"
              multiple
              accept=".pdf,.docx,.xlsx,.doc,.txt"
              onChange={(e) => handleUpload(Array.from(e.target.files))}
              className="hidden"
              id="file-upload"
              ref={fileInputRef}
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <span className="material-symbols-outlined text-[56px] text-outline-variant">cloud_upload</span>
              <p className="text-on-surface-variant text-sm mt-3">
                {uploading ? "Uploading files..." : "Drag & drop files here or click to browse"}
              </p>
              <p className="text-outline text-xs mt-1">Supports PDF, DOCX, XLSX, TXT</p>
            </label>
          </div>
        </div>
      )}

      {/* Revision Prompt */}
      {showRevisionPrompt && (
        <div className="bg-red-50 rounded-xl border border-red-200 p-6">
          <div className="flex items-start gap-3">
            <span className="material-symbols-outlined text-red-500 text-[24px]">error</span>
            <div className="flex-1">
              <h4 className="font-semibold text-red-800 text-sm">Document Verification Failed</h4>
              <p className="text-red-700 text-xs mt-1">
                The uploaded document for <strong>{currentRequiredDoc?.label}</strong> did not pass verification.
                Please review the requirements below and upload a revised document.
              </p>
              {lastVerificationResult && (
                <div className="mt-3 p-3 bg-white rounded-lg border border-red-200">
                  <p className="text-[11px] font-medium text-red-800 mb-2">Verification Result:</p>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-[11px] text-red-700">Score:</span>
                    <span className="text-[11px] font-semibold text-red-800">{lastVerificationResult.score}%</span>
                  </div>
                  {lastMissingKeywords.length > 0 && (
                    <div>
                      <p className="text-[11px] text-red-700 mb-1">Missing Requirements:</p>
                      <div className="flex flex-wrap gap-1">
                        {lastMissingKeywords.map((keyword, i) => (
                          <span key={i} className="px-2 py-0.5 bg-red-100 text-red-700 rounded text-[10px]">
                            {keyword}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
              <button
                onClick={() => {
                  setShowRevisionPrompt(false);
                  setLastVerificationResult(null);
                  setLastMissingKeywords([]);
                }}
                className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg text-xs font-medium hover:bg-red-700 transition-colors"
              >
                Upload Revised Document
              </button>
            </div>
          </div>
        </div>
      )}

      {/* All Documents Verified */}
      {allDocsVerified && (
        <div className="bg-emerald-50 rounded-xl border border-emerald-200 p-6">
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-emerald-500 text-[32px]">check_circle</span>
            <div>
              <h4 className="font-semibold text-emerald-800 text-sm">All Required Documents Verified</h4>
              <p className="text-emerald-700 text-xs mt-1">
                All {requiredDocs.length} required documents for this level have been successfully uploaded and verified.
                You can now proceed to the next level.
              </p>
            </div>
          </div>
        </div>
      )}

      {!selectedId && !loading && (
        <div className="text-center py-12">
          <span className="material-symbols-outlined text-[48px] text-outline-variant">folder_open</span>
          <p className="text-on-surface-variant mt-3 text-sm">Select a project to upload documents</p>
        </div>
      )}
    </div>
  );
}

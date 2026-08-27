import React, { useState, useEffect, useRef, useCallback } from "react";
import { projectService, chatService, painAreaService, getApiError } from "../services/api";
import "../styles/pages/AIChatPage.css";

const PORTFOLIO_SUGGESTIONS = [
  "Show quick wins",
  "Top 5 opportunities",
  "Highest manual effort department",
  "Open opportunities",
  "High priority opportunities",
  "Show roadmap",
];

const FOLLOW_UPS = {
  top: ["Show quick wins", "Which department has most hours?", "Show roadmap"],
  quick_wins: ["Top 5 opportunities", "High priority opportunities", "Show roadmap"],
  hours_department: ["Show quick wins", "Open opportunities", "Top 5 opportunities"],
  high_priority: ["Show quick wins", "Show roadmap", "Open opportunities"],
  by_status: ["Show quick wins", "Top 5 opportunities", "Highest manual effort department"],
  roadmap: ["Top 5 opportunities", "Show quick wins", "Open opportunities"],
  overview: ["Show quick wins", "Top 5 opportunities", "Show roadmap"],
};

const QUADRANT_COLORS = {
  "Quick Win": { bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200" },
  "Strategic": { bg: "bg-blue-50", text: "text-blue-700", border: "border-blue-200" },
  "Fill In": { bg: "bg-amber-50", text: "text-amber-700", border: "border-amber-200" },
  "Revisit": { bg: "bg-red-50", text: "text-red-700", border: "border-red-200" },
  "Needs Input": { bg: "bg-slate-50", text: "text-slate-500", border: "border-slate-200" },
};

const SCORE_COLORS = {
  5: "bg-emerald-100 text-emerald-700",
  4: "bg-teal-100 text-teal-700",
  3: "bg-amber-100 text-amber-700",
  2: "bg-orange-100 text-orange-700",
  1: "bg-red-100 text-red-700",
};

const INTENT_ICONS = {
  top: "leaderboard",
  quick_wins: "bolt",
  hours_department: "schedule",
  high_priority: "priority_high",
  by_status: "filter_list",
  roadmap: "route",
  overview: "dashboard",
};

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function renderMessageText(text) {
  if (!text) return null;
  const parts = text.split(/(\*\*[^*]+\*\*|\n)/g);
  return parts.map((part, i) => {
    if (part === "\n") return <br key={i} />;
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

function ScoreBadge({ score }) {
  if (score == null) {
    return <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-400 italic">N/A</span>;
  }
  return (
    <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold ${SCORE_COLORS[score] || "bg-slate-100 text-slate-600"}`}>
      {score}
    </span>
  );
}

function QuadrantBadge({ quadrant }) {
  const c = QUADRANT_COLORS[quadrant] || QUADRANT_COLORS["Needs Input"];
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border ${c.bg} ${c.text} ${c.border}`}>
      {quadrant}
    </span>
  );
}

function DataTable({ data }) {
  if (!Array.isArray(data) || data.length === 0) return null;
  const keys = Object.keys(data[0]);
  const isOppData = keys.includes("quadrant") || keys.includes("total_score");

  return (
    <div className="aichat-data-table">
      <table>
        <thead>
          <tr>
            {keys.map((k) => (
              <th key={k}>{k.replace(/_/g, " ")}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.slice(0, 20).map((row, ri) => (
            <tr key={ri}>
              {keys.map((k) => {
                const v = row[k];
                if (k === "quadrant") return <td key={k}><QuadrantBadge quadrant={v} /></td>;
                if (k === "total_score") return <td key={k}><span className="font-bold text-primary">{v}</span></td>;
                if (k === "impact_score" || k === "feasibility_score" || k === "priority_score") return <td key={k}><ScoreBadge score={v} /></td>;
                if (k === "hours" && typeof v === "number") return <td key={k}>{v.toFixed(1)}h</td>;
                return <td key={k}>{v ?? "—"}</td>;
              })}
            </tr>
          ))}
        </tbody>
      </table>
      {data.length > 20 && (
        <div className="aichat-data-hint">
          Showing first 20 of {data.length} results.
        </div>
      )}
    </div>
  );
}

export default function AIChatPopup() {

  const [isOpen, setIsOpen] = useState(false);
  const [projects, setProjects] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [assistantMode, setAssistantMode] = useState("portfolio");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [lastIntent, setLastIntent] = useState(null);
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      fetchProjects();
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleKeyDown = useCallback((e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "k") {
      e.preventDefault();
      setIsOpen((prev) => !prev);
    }
    if (e.key === "Escape") {
      setIsOpen(false);
    }
  }, []);

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  const fetchProjects = async () => {
    try {
      const res = await projectService.list();
      setProjects(res.data.results || res.data || []);
    } catch (err) {
      console.error("Failed to fetch projects:", err);
    }
  };

  const sendQuestion = async (q) => {
    if (!q.trim()) return;
    if (assistantMode === "documents" && !selectedId) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: q, ts: new Date() }]);
    setLoading(true);
    try {
      let answerMsg = "";
      let payload = null;
      let intent = null;
      if (assistantMode === "portfolio") {
        if (/roadmap|road map/i.test(q)) {
          const rm = await painAreaService.roadmap();
          const s = rm.data?.summary || {};
          const pc = s.phase_counts || {};
          answerMsg =
            `**Roadmap Summary**\n` +
            `${s.total_projects || 0} total projects · ` +
            `${pc[1] || 0} Quick Wins · ${pc[2] || 0} Strategic · ` +
            `${pc[3] || 0} Strategic · ${pc[4] || 0} Future\n` +
            `Estimated hours saved: **${s.estimated_total_hours_saved || 0}**`;
          intent = "roadmap";
        } else {
          const res = await painAreaService.assistant(q);
          answerMsg = res.data?.message || "No answer.";
          payload = res.data?.data ?? null;
          intent = res.data?.intent || null;
        }
      } else {
        const res = await chatService.ask(selectedId, q);
        answerMsg = res.data.answer;
      }
      setLastIntent(intent);
      setMessages((prev) => [...prev, { role: "assistant", content: answerMsg, data: payload, intent, ts: new Date() }]);
    } catch (err) {
      const detail = getApiError(err, "Failed to get a response. Please ensure the backend is running.");
      setMessages((prev) => [...prev, { role: "assistant", content: detail, data: null, intent: null, isError: true, failedQuestion: q, ts: new Date() }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = () => sendQuestion(input);

  const handleSuggestionClick = (q) => {
    sendQuestion(q);
  };

  const handleRetry = (q) => {
    sendQuestion(q);
  };

  const handleModeChange = (mode) => {
    setAssistantMode(mode);
    setMessages([]);
    setInput("");
    setLastIntent(null);
  };

  const handleProjectChange = (id) => {
    setSelectedId(id);
    setMessages([]);
  };

  const handleClearChat = () => {
    setMessages([]);
    setLastIntent(null);
  };

  const docQuestions = [
    "What are the main business requirements?",
    "Summarize the project objectives",
    "What risks are identified in the documents?",
    "List all stakeholders mentioned",
    "What is the expected timeline?",
  ];
  const activeQuestions =
    assistantMode === "portfolio" ? PORTFOLIO_SUGGESTIONS : docQuestions;

  const followUps = lastIntent && FOLLOW_UPS[lastIntent] ? FOLLOW_UPS[lastIntent] : null;

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="aichat-fab"
        title="AI Assistant (⌘K)"
      >
        <span className="material-symbols-outlined">smart_toy</span>
      </button>

      {/* Popup Overlay */}
      {isOpen && (
        <div className="aichat-overlay" onClick={() => setIsOpen(false)}>
          <div
            className="aichat-popup soft-shadow"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="aichat-popup-header">
              <div className="flex items-center gap-3">
                <div className="aichat-header-icon">
                  <span className="material-symbols-outlined text-[22px]">
                    smart_toy
                  </span>
                </div>
                <div>
                  <h3 className="aichat-popup-title">AI Assistant</h3>
                  <p className="aichat-popup-subtitle">
                    {assistantMode === "portfolio"
                      ? "Chat with your AI opportunity portfolio"
                      : "Chat with project knowledge"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-1">
                {messages.length > 0 && (
                  <button
                    onClick={handleClearChat}
                    className="aichat-header-action"
                    title="Clear chat"
                  >
                    <span className="material-symbols-outlined text-[18px]">delete_sweep</span>
                  </button>
                )}
                <button
                  onClick={() => setIsOpen(false)}
                  className="aichat-close-btn"
                >
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>
            </div>

            {/* Mode toggle */}
            <div className="aichat-mode-toggle">
              <button
                className={`aichat-mode-btn ${assistantMode === "portfolio" ? "aichat-mode-active" : ""}`}
                onClick={() => handleModeChange("portfolio")}
              >
                <span className="material-symbols-outlined text-[16px]">route</span>
                Portfolio
              </button>
              <button
                className={`aichat-mode-btn ${assistantMode === "documents" ? "aichat-mode-active" : ""}`}
                onClick={() => handleModeChange("documents")}
              >
                <span className="material-symbols-outlined text-[16px]">description</span>
                Documents
              </button>
            </div>

            {/* Project Selector (documents mode only) */}
            {assistantMode === "documents" && (
              <div className="aichat-selector-card">
                <select
                  value={selectedId}
                  onChange={(e) => handleProjectChange(e.target.value)}
                  className="aichat-select"
                >
                  <option value="">Select a project to chat about</option>
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.project_name} ({p.company_name})
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Messages Area */}
            <div className="aichat-messages">
              {messages.length === 0 && (
                <div className="aichat-empty">
                  <div className="aichat-empty-icon-wrapper">
                    <span className="material-symbols-outlined aichat-empty-icon">
                      smart_toy
                    </span>
                  </div>
                  <h3 className="aichat-empty-title">
                    {assistantMode === "portfolio"
                      ? "AI Portfolio Assistant"
                      : "AI Document Assistant"}
                  </h3>
                  <p className="aichat-empty-desc">
                    {assistantMode === "portfolio"
                      ? "Ask about your AI opportunity portfolio — quick wins, priorities, departments and more"
                      : selectedId
                      ? "Ask questions about this project's uploaded documents"
                      : "Select a project above to start chatting"}
                  </p>

                  {(assistantMode === "portfolio" ||
                    (assistantMode === "documents" && selectedId)) && (
                    <div className="aichat-suggestions">
                      {activeQuestions.map((q) => (
                        <button
                          key={q}
                          onClick={() => handleSuggestionClick(q)}
                          className="aichat-suggestion-btn"
                        >
                          {q}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`aichat-msg-row ${msg.role === "user" ? "aichat-msg-row-user" : "aichat-msg-row-assistant"}`}
                >
                  {msg.role === "assistant" && (
                    <div className="aichat-avatar">
                      <span className="material-symbols-outlined text-[16px]">
                        {msg.isError ? "error" : (INTENT_ICONS[msg.intent] || "smart_toy")}
                      </span>
                    </div>
                  )}
                  <div className="aichat-msg-col">
                    <div
                      className={`aichat-bubble ${
                        msg.role === "user"
                          ? "aichat-bubble-user"
                          : msg.isError
                          ? "aichat-bubble-error"
                          : "aichat-bubble-assistant"
                      }`}
                    >
                      {renderMessageText(msg.content)}
                      {msg.role === "assistant" && Array.isArray(msg.data) && msg.data.length > 0 && (
                        <DataTable data={msg.data} />
                      )}
                      {msg.role === "assistant" && msg.data && !Array.isArray(msg.data) && typeof msg.data === "object" && (
                        <div className="aichat-stats-grid">
                          {Object.entries(msg.data).map(([k, v]) => (
                            <div key={k} className="aichat-stat-item">
                              <span className="aichat-stat-label">{k.replace(/_/g, " ")}</span>
                              <span className="aichat-stat-value">{typeof v === "number" ? v.toLocaleString() : v ?? "—"}</span>
                            </div>
                          ))}
                        </div>
                      )}
                      {msg.isError && msg.failedQuestion && (
                        <button
                          onClick={() => handleRetry(msg.failedQuestion)}
                          className="aichat-retry-btn"
                        >
                          <span className="material-symbols-outlined text-[14px]">refresh</span>
                          Retry
                        </button>
                      )}
                    </div>
                    <span className="aichat-timestamp">{formatTime(msg.ts)}</span>
                  </div>
                </div>
              ))}

              {loading && (
                <div className="aichat-msg-row aichat-msg-row-assistant">
                  <div className="aichat-avatar">
                    <span className="material-symbols-outlined text-[16px]">smart_toy</span>
                  </div>
                  <div className="aichat-typing">
                    <div className="aichat-typing-dots">
                      <div className="aichat-typing-dot" style={{ animationDelay: "0ms" }} />
                      <div className="aichat-typing-dot" style={{ animationDelay: "150ms" }} />
                      <div className="aichat-typing-dot" style={{ animationDelay: "300ms" }} />
                    </div>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Follow-up suggestions */}
            {followUps && !loading && messages.length > 0 && (
              <div className="aichat-followups">
                {followUps.map((q) => (
                  <button
                    key={q}
                    onClick={() => handleSuggestionClick(q)}
                    className="aichat-followup-btn"
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}

            {/* Input Area */}
            <div className="aichat-input-area">
              <div className="aichat-input-row">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
                  placeholder={
                    assistantMode === "portfolio"
                      ? "Ask about your AI opportunities..."
                      : selectedId
                      ? "Ask a question about the project documents..."
                      : "Select a project first"
                  }
                  disabled={assistantMode === "documents" && !selectedId}
                  className="aichat-input"
                />
                <button
                  onClick={handleSend}
                  disabled={
                    loading ||
                    !input.trim() ||
                    (assistantMode === "documents" && !selectedId)
                  }
                  className="aichat-send-btn"
                >
                  {loading ? (
                    <span className="material-symbols-outlined aichat-send-icon animate-spin">progress_activity</span>
                  ) : (
                    <span className="material-symbols-outlined aichat-send-icon">send</span>
                  )}
                </button>
              </div>
              <div className="aichat-input-hint">
                <span className="material-symbols-outlined text-[12px]">keyboard</span>
                ⌘K to toggle · Enter to send
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

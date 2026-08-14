import React, { useState, useEffect, useRef } from "react";
import { projectService, chatService, painAreaService, getApiError } from "../services/api";
import { useAuth } from "../context/AuthContext";
import "../styles/pages/AIChatPage.css";

const PORTFOLIO_SUGGESTIONS = [
  "Show quick wins",
  "Top 5 opportunities",
  "Highest manual effort department",
  "Open opportunities",
  "High priority opportunities",
  "Show roadmap",
];

export default function AIChatPopup() {
  const { plan } = useAuth();
  const aiEnabled = !plan || Boolean(plan.features?.custom_rag);

  const [isOpen, setIsOpen] = useState(false);
  const [projects, setProjects] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [assistantMode, setAssistantMode] = useState("portfolio");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      fetchProjects();
    }
  }, [isOpen]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchProjects = async () => {
    try {
      const res = await projectService.list();
      setProjects(res.data.results || res.data || []);
    } catch (err) {
      console.error("Failed to fetch projects:", err);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    if (assistantMode === "documents" && !selectedId) return;
    const q = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setLoading(true);
    try {
      let answerMsg = "";
      let payload = null;
      if (assistantMode === "portfolio") {
        if (/roadmap|road map/i.test(q)) {
          const rm = await painAreaService.roadmap();
          const s = rm.data?.summary || {};
          const pc = s.phase_counts || {};
          answerMsg =
            `Roadmap summary: ${s.total_projects || 0} total projects · ` +
            `${pc[1] || 0} Quick Wins · ${pc[2] || 0} Major Projects · ` +
            `${pc[3] || 0} Strategic · ${pc[4] || 0} Future · ` +
            `${s.estimated_total_hours_saved || 0} hrs saved.`;
        } else {
          const res = await painAreaService.assistant(q);
          answerMsg = res.data?.message || "No answer.";
          payload = res.data?.data ?? null;
        }
      } else {
        const res = await chatService.ask(selectedId, q);
        answerMsg = res.data.answer;
      }
      setMessages((prev) => [...prev, { role: "assistant", content: answerMsg, data: payload }]);
    } catch (err) {
      const detail = getApiError(
        err,
        "Failed to get a response. Please ensure the backend is running."
      );
      setMessages((prev) => [...prev, { role: "assistant", content: detail, data: null }]);
    } finally {
      setLoading(false);
    }
  };

  const handleModeChange = (mode) => {
    setAssistantMode(mode);
    setMessages([]);
    setInput("");
  };

  const handleProjectChange = (id) => {
    setSelectedId(id);
    setMessages([]);
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

  return (
    <>
      {/* Floating Button - Bottom Right of all pages */}
      <button
        onClick={() => setIsOpen(true)}
        className="aichat-fab"
        title="AI Assistant"
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
                <span className="material-symbols-outlined text-primary text-[28px]">
                  smart_toy
                </span>
                <div>
                  <h3 className="aichat-popup-title">AI Assistant</h3>
                  <p className="aichat-popup-subtitle">
                    {assistantMode === "portfolio"
                      ? "Chat with your AI opportunity portfolio"
                      : "Chat with project knowledge"}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="aichat-close-btn"
              >
                <span className="material-symbols-outlined">close</span>
              </button>
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

            {/* Locked State */}
            {!aiEnabled ? (
              <div className="aichat-locked-card">
                <span className="material-symbols-outlined aichat-locked-icon">
                  lock
                </span>
                <h3 className="aichat-locked-title">
                  Custom RAG not available on your plan
                </h3>
                <p className="aichat-locked-desc">
                  This feature requires the custom_rag add-on. Ask your company admin
                  to upgrade the subscription to enable AI document chat.
                </p>
              </div>
            ) : (
              <>
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
                      <span className="material-symbols-outlined aichat-empty-icon">
                        smart_toy
                      </span>
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
                              onClick={() => setInput(q)}
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
                      className={`flex ${
                        msg.role === "user" ? "justify-end" : "justify-start"
                      }`}
                    >
                      <div
                        className={`aichat-bubble ${
                          msg.role === "user"
                            ? "aichat-bubble-user"
                            : "aichat-bubble-assistant"
                        }`}
                      >
                        {msg.content}
                        {msg.role === "assistant" && Array.isArray(msg.data) && msg.data.length > 0 && (
                          <div className="aichat-data-table">
                            <table>
                              <thead>
                                <tr>
                                  {Object.keys(msg.data[0]).map((k) => (
                                    <th key={k}>{k.replace(/_/g, " ")}</th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody>
                                {msg.data.slice(0, 20).map((row, ri) => (
                                  <tr key={ri}>
                                    {Object.keys(msg.data[0]).map((k) => (
                                      <td key={k}>{row[k] ?? "—"}</td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                            {msg.data.length > 20 && (
                              <div className="aichat-data-hint">
                                Showing first 20 of {msg.data.length} results.
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}

                  {loading && (
                    <div className="flex justify-start">
                      <div className="aichat-typing">
                        <div className="aichat-typing-dots">
                          <div
                            className="aichat-typing-dot"
                            style={{ animationDelay: "0ms" }}
                          />
                          <div
                            className="aichat-typing-dot"
                            style={{ animationDelay: "150ms" }}
                          />
                          <div
                            className="aichat-typing-dot"
                            style={{ animationDelay: "300ms" }}
                          />
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>

                {/* Input Area */}
                <div className="aichat-input-area">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleSend()}
                      placeholder={
                        assistantMode === "portfolio"
                          ? "Ask about your AI opportunities..."
                          : selectedId
                          ? "Ask a question about the project documents..."
                          : "Select a project first"
                      }
                      disabled={
                        !aiEnabled ||
                        (assistantMode === "documents" && !selectedId)
                      }
                      className="aichat-input"
                    />
                    <button
                      onClick={handleSend}
                      disabled={
                        loading ||
                        !input.trim() ||
                        !aiEnabled ||
                        (assistantMode === "documents" && !selectedId)
                      }
                      className="aichat-send-btn"
                    >
                      <span className="material-symbols-outlined aichat-send-icon">
                        send
                      </span>
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
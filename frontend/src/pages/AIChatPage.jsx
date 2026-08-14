import React, { useState, useEffect, useRef } from "react";
import { projectService, chatService, getApiError } from "../services/api";
import { useAuth } from "../context/AuthContext";
import "../styles/pages/AIChatPage.css";

export default function AIChatPopup() {
  const { plan } = useAuth();
  const aiEnabled = !plan || Boolean(plan.features?.custom_rag);

  const [isOpen, setIsOpen] = useState(false);
  const [projects, setProjects] = useState([]);
  const [selectedId, setSelectedId] = useState("");
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
    if (!input.trim() || !selectedId) return;
    const q = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setLoading(true);
    try {
      const res = await chatService.ask(selectedId, q);
      setMessages((prev) => [...prev, { role: "assistant", content: res.data.answer }]);
    } catch (err) {
      const detail = getApiError(
        err,
        "Failed to get a response. Please ensure the backend is running and documents are uploaded."
      );
      setMessages((prev) => [...prev, { role: "assistant", content: detail }]);
    } finally {
      setLoading(false);
    }
  };

  const handleProjectChange = (id) => {
    setSelectedId(id);
    setMessages([]);
  };

  const suggestedQuestions = [
    "What are the main business requirements?",
    "Summarize the project objectives",
    "What risks are identified in the documents?",
    "List all stakeholders mentioned",
    "What is the expected timeline?",
  ];

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
                  <p className="aichat-popup-subtitle">Chat with project knowledge</p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="aichat-close-btn"
              >
                <span className="material-symbols-outlined">close</span>
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
                {/* Project Selector */}
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

                {/* Messages Area */}
                <div className="aichat-messages">
                  {messages.length === 0 && (
                    <div className="aichat-empty">
                      <span className="material-symbols-outlined aichat-empty-icon">
                        smart_toy
                      </span>
                      <h3 className="aichat-empty-title">AI Document Assistant</h3>
                      <p className="aichat-empty-desc">
                        {selectedId
                          ? "Ask questions about this project's uploaded documents"
                          : "Select a project above to start chatting"}
                      </p>

                      {selectedId && (
                        <div className="aichat-suggestions">
                          {suggestedQuestions.map((q) => (
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
                        selectedId
                          ? "Ask a question about the project documents..."
                          : "Select a project first"
                      }
                      disabled={!selectedId || !aiEnabled}
                      className="aichat-input"
                    />
                    <button
                      onClick={handleSend}
                      disabled={
                        !input.trim() || !selectedId || loading || !aiEnabled
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
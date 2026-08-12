import React, { useState, useEffect, useRef } from "react";
import { projectService, chatService, getApiError } from "../services/api";
import { useAuth } from "../context/AuthContext";
import TopHeader from "../components/TopHeader";
import "../styles/pages/AIChatPage.css";

export default function AIChatPage({ projectId, onSelectProject }) {
  const { plan } = useAuth();
  const aiEnabled = !plan || Boolean(plan.features?.custom_rag);
  const [projects, setProjects] = useState([]);
  const [selectedId, setSelectedId] = useState(projectId || "");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [fetchingProjects, setFetchingProjects] = useState(true);
  const chatEndRef = useRef(null);

  useEffect(() => { fetchProjects(); }, []);
  useEffect(() => { if (projectId) setSelectedId(projectId); }, [projectId]);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const fetchProjects = async () => {
    try {
      const res = await projectService.list();
      setProjects(res.data.results || res.data || []);
    } catch (err) {
      console.error("Failed to fetch projects:", err);
    } finally {
      setFetchingProjects(false);
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
      const detail = getApiError(err, "Failed to get a response. Please ensure the backend is running and documents are uploaded.");
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
    <div className="space-y-6">
      <TopHeader title="AI Assistant" subtitle="Chat with project knowledge" />

      {!aiEnabled && (
        <div className="aichat-locked-card soft-shadow">
          <span className="material-symbols-outlined aichat-locked-icon">lock</span>
          <h3 className="aichat-locked-title">
            Custom RAG not available on your plan
          </h3>
          <p className="aichat-locked-desc">
            This feature requires the custom_rag add-on. Ask your company admin to upgrade the
            subscription to enable AI document chat.
          </p>
        </div>
      )}

      {/* Project Selector */}
      <div className="aichat-selector-card soft-shadow">
        <select
          value={selectedId}
          onChange={(e) => handleProjectChange(e.target.value)}
          className="aichat-select"
        >
          <option value="">Select a project to chat about</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.project_name} ({p.company_name})</option>
          ))}
        </select>
      </div>

      {/* Chat Area */}
      <div className="aichat-card soft-shadow">
        <div className="aichat-messages">
          {messages.length === 0 && (
            <div className="aichat-empty">
              <span className="material-symbols-outlined aichat-empty-icon">smart_toy</span>
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
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`aichat-bubble ${
                msg.role === "user"
                  ? "aichat-bubble-user"
                  : "aichat-bubble-assistant"
              }`}>
                {msg.content}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
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

        {/* Input */}
        <div className="aichat-input-area">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder={!aiEnabled ? "Custom RAG is disabled on this plan" : selectedId ? "Ask a question about the project documents..." : "Select a project first"}
              disabled={!selectedId || !aiEnabled}
              className="aichat-input"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || !selectedId || loading || !aiEnabled}
              className="aichat-send-btn"
            >
              <span className="material-symbols-outlined aichat-send-icon">send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

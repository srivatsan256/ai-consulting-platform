import React, { useState, useEffect, useRef } from "react";
import { projectService, chatService, getApiError } from "../services/api";
import { useAuth } from "../context/AuthContext";
import TopHeader from "../components/TopHeader";

export default function ClientChatPage({ projectId }) {
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
    "What is the status of this project?",
    "Summarize the project objectives",
    "What are the main requirements?",
    "What risks are identified in the documents?",
    "What is the expected timeline?",
  ];

  return (
    <div className="space-y-6">
      <TopHeader title="AI Assistant" subtitle="Chat with your project knowledge" />

      {!aiEnabled && (
        <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-8 text-center">
          <span className="material-symbols-outlined text-[56px] text-outline-variant">lock</span>
          <h3 className="font-headline-sm text-lg font-bold text-on-surface mt-3">
            Custom RAG not available on your plan
          </h3>
          <p className="text-on-surface-variant text-sm mt-1 max-w-md mx-auto">
            This feature requires the custom_rag add-on. Ask your company admin to upgrade the
            subscription to enable AI document chat.
          </p>
        </div>
      )}

      {/* Project Selector */}
      <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-4">
        <select
          value={selectedId}
          onChange={(e) => handleProjectChange(e.target.value)}
          className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
        >
          <option value="">Select a project to chat about</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.project_name} ({p.company_name})</option>
          ))}
        </select>
      </div>

      {/* Chat Area */}
      <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 overflow-hidden">
        <div className="h-[500px] overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-16">
              <span className="material-symbols-outlined text-[56px] text-outline-variant">smart_toy</span>
              <h3 className="font-headline-sm text-lg font-bold text-on-surface mt-3">AI Document Assistant</h3>
              <p className="text-on-surface-variant text-sm mt-1 max-w-md mx-auto">
                {selectedId
                  ? "Ask questions about this project's uploaded documents"
                  : "Select a project above to start chatting"}
              </p>
              {selectedId && (
                <div className="flex flex-wrap gap-2 justify-center mt-6">
                  {suggestedQuestions.map((q) => (
                    <button
                      key={q}
                      onClick={() => setInput(q)}
                      className="px-3 py-2 bg-surface-container-low rounded-lg border border-outline-variant/30 text-xs text-on-surface-variant hover:border-primary/50 hover:bg-primary/5 transition-colors"
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
              <div className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-primary text-on-primary rounded-br-md"
                  : "bg-surface-container-low border border-outline-variant/20 text-on-surface rounded-bl-md"
              }`}>
                {msg.content}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-surface-container-low border border-outline-variant/20 px-4 py-3 rounded-2xl rounded-bl-md">
                <div className="flex gap-1.5">
                  <div className="w-2 h-2 bg-outline-variant rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <div className="w-2 h-2 bg-outline-variant rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <div className="w-2 h-2 bg-outline-variant rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-outline-variant/20 p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder={!aiEnabled ? "Custom RAG is disabled on this plan" : selectedId ? "Ask a question about the project documents..." : "Select a project first"}
              disabled={!selectedId || !aiEnabled}
              className="flex-1 px-4 py-3 rounded-xl border border-outline-variant/40 text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 disabled:opacity-50"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || !selectedId || loading || !aiEnabled}
              className="px-5 py-3 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 disabled:opacity-50 transition-all flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-[18px]">send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

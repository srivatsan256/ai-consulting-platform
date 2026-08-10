import React, { useState, useEffect, useCallback } from "react";
import { workflowService, getApiError } from "../services/api";
import TopHeader from "../components/TopHeader";

const inputCls =
  "w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20";
const labelCls =
  "block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5";

const WORKFLOW_STATUS = {
  draft: { label: "Draft", icon: "edit_note", color: "text-on-surface-variant" },
  active: { label: "Active", icon: "play_circle", color: "text-emerald-500" },
  inactive: { label: "Inactive", icon: "pause_circle", color: "text-amber-500" },
};

const EXECUTION_STATUS = {
  running: { label: "Running", icon: "progress_activity", color: "text-primary" },
  completed: { label: "Completed", icon: "check_circle", color: "text-emerald-500" },
  failed: { label: "Failed", icon: "error", color: "text-red-500" },
  cancelled: { label: "Cancelled", icon: "cancel", color: "text-on-surface-variant" },
};

const HISTORY_EVENT_STYLE = {
  started: { icon: "play_arrow", color: "text-primary", bg: "bg-primary/10" },
  step_started: { icon: "flag", color: "text-sky-500", bg: "bg-sky-500/10" },
  step_completed: { icon: "task_alt", color: "text-emerald-500", bg: "bg-emerald-500/10" },
  approval_requested: { icon: "mark_email_unread", color: "text-amber-500", bg: "bg-amber-500/10" },
  approved: { icon: "verified", color: "text-emerald-500", bg: "bg-emerald-500/10" },
  rejected: { icon: "block", color: "text-red-500", bg: "bg-red-500/10" },
  completed: { icon: "check_circle", color: "text-emerald-500", bg: "bg-emerald-500/10" },
  failed: { icon: "error", color: "text-red-500", bg: "bg-red-500/10" },
  cancelled: { icon: "cancel", color: "text-on-surface-variant", bg: "bg-on-surface-variant/10" },
  resumed: { icon: "play_circle", color: "text-emerald-500", bg: "bg-emerald-500/10" },
  comment: { icon: "comment", color: "text-on-surface-variant", bg: "bg-on-surface-variant/10" },
};

const STEP_TYPE_LABEL = {
  approval: "Approval",
  notification: "Notification",
  task: "Task",
  condition: "Condition",
  wait: "Wait",
};

const formatDate = (v) => (v ? new Date(v).toLocaleString() : "N/A");

function statusBadge(status) {
  const s = EXECUTION_STATUS[status] || EXECUTION_STATUS.running;
  return (
    <span className={`inline-flex items-center gap-1 text-[11px] font-semibold ${s.color}`}>
      <span className="material-symbols-outlined text-[14px]">{s.icon}</span>
      {s.label}
    </span>
  );
}

function workflowBadge(status) {
  const s = WORKFLOW_STATUS[status] || WORKFLOW_STATUS.draft;
  return (
    <span className={`inline-flex items-center gap-1 text-[11px] font-semibold ${s.color}`}>
      <span className="material-symbols-outlined text-[14px]">{s.icon}</span>
      {s.label}
    </span>
  );
}

// ─────────────────────────────────────────────────────────────
// History Timeline
// ─────────────────────────────────────────────────────────────
function HistoryTimeline({ events }) {
  if (!events.length) {
    return (
      <div className="text-center py-10">
        <span className="material-symbols-outlined text-[40px] text-outline-variant">history</span>
        <p className="text-on-surface-variant mt-3 text-sm">No history events yet</p>
        <p className="text-xs text-outline mt-1">
          Start or complete an execution to record workflow history.
        </p>
      </div>
    );
  }

  return (
    <div className="relative">
      <div className="absolute left-[15px] top-2 bottom-2 w-px bg-outline-variant/40" />
      <div className="space-y-5">
        {events.map((ev) => {
          const style = HISTORY_EVENT_STYLE[ev.event_type] || HISTORY_EVENT_STYLE.comment;
          return (
            <div key={ev.id} className="relative flex gap-4 pl-0">
              <div className="z-10 flex items-center justify-center w-8 h-8 rounded-full shrink-0 bg-white border border-outline-variant/30">
                <span className={`material-symbols-outlined text-[16px] ${style.color}`}>{style.icon}</span>
              </div>
              <div className="flex-1 min-w-0 pt-0.5">
                <div className="flex items-center justify-between gap-2 flex-wrap">
                  <p className="text-sm font-semibold text-on-surface">
                    {ev.event_type_display}
                    {ev.step_name && (
                      <span className="text-on-surface-variant font-normal"> · {ev.step_name}</span>
                    )}
                  </p>
                  <span className="text-[11px] text-outline">{formatDate(ev.created_at)}</span>
                </div>
                {ev.message && <p className="text-xs text-on-surface-variant mt-1">{ev.message}</p>}
                <p className="text-[11px] text-outline mt-1">
                  by {ev.actor_name}
                  {ev.workflow_execution ? ` · Execution #${ev.workflow_execution}` : ""}
                </p>
                {Object.keys(ev.metadata || {}).length > 0 && (
                  <pre className="mt-2 text-[10px] bg-surface-container-low rounded-lg p-2 overflow-x-auto text-on-surface-variant">
                    {JSON.stringify(ev.metadata, null, 2)}
                  </pre>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Workflow Detail Panel
// ─────────────────────────────────────────────────────────────
function WorkflowDetail({ workflow, onBack, onChanged }) {
  const [subTab, setSubTab] = useState("overview");
  const [executions, setExecutions] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [historyFilter, setHistoryFilter] = useState("");

  useEffect(() => {
    setLoading(true);
    Promise.allSettled([
      workflowService.executions(workflow.id),
      workflowService.workflowHistory(workflow.id),
    ]).then(([eRes, hRes]) => {
      if (eRes.status === "fulfilled") setExecutions(eRes.value.data || []);
      if (hRes.status === "fulfilled") setHistory(hRes.value.data || []);
      setLoading(false);
    });
  }, [workflow.id]);

  const filteredHistory = historyFilter
    ? history.filter((h) => h.event_type === historyFilter)
    : history;

  const toggleStatus = async () => {
    try {
      if (workflow.status === "active") await workflowService.deactivate(workflow.id);
      else await workflowService.activate(workflow.id);
      onChanged();
    } catch (err) {
      alert(getApiError(err, "Failed to update workflow."));
    }
  };

  const completeExecution = async (execution) => {
    try {
      await workflowService.completeExecution(execution.id);
      const res = await workflowService.workflowHistory(workflow.id);
      setHistory(res.data || []);
      const eRes = await workflowService.executions(workflow.id);
      setExecutions(eRes.data || []);
    } catch (err) {
      alert(getApiError(err, "Failed to complete execution."));
    }
  };

  return (
    <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 overflow-hidden">
      <div className="p-6 border-b border-outline-variant/20">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="flex items-start gap-3">
            <button
              onClick={onBack}
              className="p-2 rounded-lg hover:bg-surface-container-low text-on-surface-variant"
              title="Back to workflows"
            >
              <span className="material-symbols-outlined">arrow_back</span>
            </button>
            <div>
              <h3 className="font-semibold text-on-surface text-lg">{workflow.name}</h3>
              <p className="text-xs text-on-surface-variant mt-0.5">
                {workflow.project_name || `Project #${workflow.project}`} · Trigger: {workflow.trigger_event}
              </p>
              {workflow.description && (
                <p className="text-sm text-on-surface-variant mt-2">{workflow.description}</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-3">
            {workflowBadge(workflow.status)}
            <button
              onClick={toggleStatus}
              className={`px-4 py-2 rounded-xl text-xs font-bold text-white transition-all hover:opacity-90 ${
                workflow.status === "active" ? "bg-amber-500" : "bg-emerald-500"
              }`}
            >
              {workflow.status === "active" ? "Deactivate" : "Activate"}
            </button>
          </div>
        </div>
        <div className="flex gap-2 mt-5 border-b border-outline-variant/20 -mb-px">
          {[
            ["overview", "Overview"],
            ["executions", `Executions (${executions.length})`],
            ["history", `History (${history.length})`],
          ].map(([key, label]) => (
            <button
              key={key}
              onClick={() => setSubTab(key)}
              className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-colors ${
                subTab === key ? "border-primary text-primary" : "border-transparent text-on-surface-variant hover:text-on-surface"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <div className="p-6">
        {loading ? (
          <p className="text-sm text-on-surface-variant">Loading...</p>
        ) : subTab === "overview" ? (
          <div>
            <h4 className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider mb-3">
              Steps ({workflow.steps.length})
            </h4>
            {workflow.steps.length === 0 ? (
              <p className="text-sm text-on-surface-variant">No steps defined yet.</p>
            ) : (
              <div className="space-y-2">
                {workflow.steps.map((step) => (
                  <div key={step.id} className="flex items-center gap-3 p-3 rounded-lg bg-surface-container-low">
                    <span className="w-7 h-7 rounded-full bg-primary/10 text-primary flex items-center justify-center text-xs font-bold">
                      {step.order}
                    </span>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-on-surface">{step.name}</p>
                      <p className="text-[11px] text-on-surface-variant">
                        {STEP_TYPE_LABEL[step.step_type] || step.step_type}
                        {step.assignee_role ? ` · ${step.assignee_role}` : ""}
                      </p>
                    </div>
                    <span className="material-symbols-outlined text-outline-variant">drag_indicator</span>
                  </div>
                ))}
              </div>
            )}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-lg bg-surface-container-low">
                <p className="text-[11px] text-on-surface-variant uppercase tracking-wider">Status</p>
                <p className="text-sm font-semibold text-on-surface mt-1">{workflow.status}</p>
              </div>
              <div className="p-4 rounded-lg bg-surface-container-low">
                <p className="text-[11px] text-on-surface-variant uppercase tracking-wider">Trigger Event</p>
                <p className="text-sm font-semibold text-on-surface mt-1 break-words">{workflow.trigger_event}</p>
              </div>
              <div className="p-4 rounded-lg bg-surface-container-low">
                <p className="text-[11px] text-on-surface-variant uppercase tracking-wider">Created By</p>
                <p className="text-sm font-semibold text-on-surface mt-1">{workflow.created_by_name || "N/A"}</p>
              </div>
            </div>
          </div>
        ) : subTab === "executions" ? (
          executions.length === 0 ? (
            <div className="text-center py-10">
              <span className="material-symbols-outlined text-[40px] text-outline-variant">play_circle</span>
              <p className="text-on-surface-variant mt-3 text-sm">No executions yet</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-[11px] uppercase tracking-wider text-on-surface-variant border-b border-outline-variant/20 bg-surface-container-low">
                    <th className="px-4 py-3">ID</th>
                    <th className="px-4 py-3">Entity</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Initiated By</th>
                    <th className="px-4 py-3">Started</th>
                    <th className="px-4 py-3">Completed</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {executions.map((exec) => (
                    <tr key={exec.id} className="border-b border-outline-variant/10">
                      <td className="px-4 py-3 font-medium text-on-surface">#{exec.id}</td>
                      <td className="px-4 py-3 text-on-surface-variant">
                        {exec.entity_type} #{exec.entity_id}
                      </td>
                      <td className="px-4 py-3">{statusBadge(exec.status)}</td>
                      <td className="px-4 py-3 text-on-surface-variant">{exec.initiated_by_name}</td>
                      <td className="px-4 py-3 text-xs text-on-surface-variant">{formatDate(exec.started_at)}</td>
                      <td className="px-4 py-3 text-xs text-on-surface-variant">{formatDate(exec.completed_at)}</td>
                      <td className="px-4 py-3 text-right">
                        {exec.status === "running" && (
                          <button
                            onClick={() => completeExecution(exec)}
                            className="px-3 py-1.5 rounded-lg bg-emerald-500 text-white text-xs font-semibold hover:opacity-90"
                          >
                            Complete
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        ) : (
          <div>
            <div className="flex items-center justify-between mb-5">
              <p className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">
                Audit trail of every event on this workflow
              </p>
              <select
                value={historyFilter}
                onChange={(e) => setHistoryFilter(e.target.value)}
                className="px-3 py-2 rounded-lg border border-outline-variant/40 bg-surface-container-low text-xs focus:outline-none focus:border-primary max-w-[180px]"
              >
                <option value="">All event types</option>
                {Object.entries(HISTORY_EVENT_STYLE).map(([key, style]) => (
                  <option key={key} value={key}>
                    {key.replace(/_/g, " ")}
                  </option>
                ))}
              </select>
            </div>
            <HistoryTimeline events={filteredHistory} />
          </div>
        )}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Main Page
// ─────────────────────────────────────────────────────────────
export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");

  const fetchWorkflows = useCallback(async () => {
    setLoading(true);
    const params = {};
    if (statusFilter) params.status = statusFilter;
    try {
      const res = await workflowService.list(params);
      const data = res.data.results || res.data || [];
      setWorkflows(data);
      setSelected((prev) =>
        prev ? data.find((w) => w.id === prev.id) || null : prev
      );
    } catch (err) {
      console.error("Failed to fetch workflows:", err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    fetchWorkflows();
  }, [fetchWorkflows]);

  const deleteWorkflow = async (workflow) => {
    if (!window.confirm(`Delete workflow "${workflow.name}"?`)) return;
    try {
      await workflowService.delete(workflow.id);
      if (selected?.id === workflow.id) setSelected(null);
      fetchWorkflows();
    } catch (err) {
      alert(getApiError(err, "Failed to delete workflow."));
    }
  };

  return (
    <div className="space-y-6">
      <TopHeader
        title="Workflows"
        subtitle="Automation flows and execution history"
      />

      {selected ? (
        <WorkflowDetail
          workflow={selected}
          onBack={() => setSelected(null)}
          onChanged={fetchWorkflows}
        />
      ) : (
        <>
          <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-4 flex items-center justify-between flex-wrap gap-3">
            <div>
              <h3 className="font-semibold text-on-surface text-sm">All Workflows</h3>
              <p className="text-xs text-on-surface-variant mt-0.5">
                Select a workflow to view its steps, executions and history.
              </p>
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 rounded-lg border border-outline-variant/40 bg-surface-container-low text-xs focus:outline-none focus:border-primary"
            >
              <option value="">All statuses</option>
              {Object.entries(WORKFLOW_STATUS).map(([k, v]) => (
                <option key={k} value={k}>
                  {v.label}
                </option>
              ))}
            </select>
          </div>

          {loading ? (
            <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-6">
              <p className="text-sm text-on-surface-variant">Loading workflows...</p>
            </div>
          ) : workflows.length === 0 ? (
            <div className="bg-white rounded-xl soft-shadow border border-outline-variant/20 text-center py-14">
              <span className="material-symbols-outlined text-[48px] text-outline-variant">account_tree</span>
              <p className="text-on-surface-variant mt-3 text-sm">No workflows found</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {workflows.map((workflow) => (
                <div
                  key={workflow.id}
                  className="bg-white rounded-xl soft-shadow border border-outline-variant/20 p-5 flex flex-col cursor-pointer hover:border-primary/40 transition-colors"
                  onClick={() => setSelected(workflow)}
                >
                  <div className="flex items-start justify-between mb-3">
                    {workflowBadge(workflow.status)}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteWorkflow(workflow);
                      }}
                      className="p-1.5 rounded-lg hover:bg-surface-container-low text-on-surface-variant hover:text-red-500"
                    >
                      <span className="material-symbols-outlined text-[18px]">delete</span>
                    </button>
                  </div>
                  <h4 className="font-semibold text-on-surface text-sm">{workflow.name}</h4>
                  <p className="text-xs text-on-surface-variant mt-1 flex-1">
                    {workflow.description || "No description"}
                  </p>
                  <div className="mt-4 pt-3 border-t border-outline-variant/10 flex items-center justify-between text-xs text-on-surface-variant">
                    <span className="inline-flex items-center gap-1">
                      <span className="material-symbols-outlined text-[14px]">steps</span>
                      {workflow.steps.length} steps
                    </span>
                    <span className="inline-flex items-center gap-1">
                      <span className="material-symbols-outlined text-[14px]">history</span>
                      {workflow.execution_count || 0} runs
                    </span>
                    <span className="inline-flex items-center gap-1">
                      <span className="material-symbols-outlined text-[14px]">bolt</span>
                      {workflow.trigger_event}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

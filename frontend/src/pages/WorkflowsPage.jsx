import React, { useState, useEffect, useCallback } from "react";
import { workflowService, getApiError } from "../services/api";
import TopHeader from "../components/TopHeader";
import "../styles/pages/WorkflowsPage.css";

const inputCls = "workflows-input";
const labelCls = "workflows-label";

// UI display maps only (not data)
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

const STEP_TYPES = ["approval", "notification", "task", "condition", "wait"];

const emptyStep = () => ({
  name: "",
  step_type: "task",
  assignee_role: "",
  order: 1,
});

const emptyForm = () => ({
  name: "",
  description: "",
  project: "",
  trigger_event: "",
  status: "draft",
  steps: [emptyStep()],
});

const formatDate = (v) => (v ? new Date(v).toLocaleString() : "N/A");

function statusBadge(status) {
  const s = EXECUTION_STATUS[status] || EXECUTION_STATUS.running;
  return (
    <span className={`workflows-badge ${s.color}`}>
      <span className="material-symbols-outlined text-[14px]">{s.icon}</span>
      {s.label}
    </span>
  );
}

function workflowBadge(status) {
  const s = WORKFLOW_STATUS[status] || WORKFLOW_STATUS.draft;
  return (
    <span className={`workflows-badge ${s.color}`}>
      <span className="material-symbols-outlined text-[14px]">{s.icon}</span>
      {s.label}
    </span>
  );
}

// ─────────────────────────────────────────────────────────────
// History Timeline (API data only)
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
              <div className="workflows-event-icon">
                <span className={`material-symbols-outlined text-[16px] ${style.color}`}>{style.icon}</span>
              </div>
              <div className="flex-1 min-w-0 pt-0.5">
                <div className="flex items-center justify-between gap-2 flex-wrap">
                  <p className="text-sm font-semibold text-on-surface">
                    {ev.event_type_display || ev.event_type}
                    {ev.step_name && (
                      <span className="text-on-surface-variant font-normal"> · {ev.step_name}</span>
                    )}
                  </p>
                  <span className="text-[11px] text-outline">{formatDate(ev.created_at)}</span>
                </div>
                {ev.message && <p className="text-xs text-on-surface-variant mt-1">{ev.message}</p>}
                <p className="text-[11px] text-outline mt-1">
                  by {ev.actor_name || "System"}
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
// Create / Edit Modal → POST / PATCH to Django
// ─────────────────────────────────────────────────────────────
function WorkflowFormModal({ initial, onClose, onSaved }) {
  const isEdit = Boolean(initial?.id);
  const [form, setForm] = useState(() => {
    if (!initial) return emptyForm();
    return {
      name: initial.name || "",
      description: initial.description || "",
      project: initial.project || "",
      trigger_event: initial.trigger_event || "",
      status: initial.status || "draft",
      steps:
        initial.steps?.length > 0
          ? initial.steps.map((s, i) => ({
              id: s.id,
              name: s.name || "",
              step_type: s.step_type || "task",
              assignee_role: s.assignee_role || "",
              order: s.order ?? i + 1,
            }))
          : [emptyStep()],
    };
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const updateField = (key, value) => setForm((f) => ({ ...f, [key]: value }));

  const updateStep = (idx, key, value) => {
    setForm((f) => {
      const steps = [...f.steps];
      steps[idx] = { ...steps[idx], [key]: value };
      return { ...f, steps };
    });
  };

  const addStep = () => {
    setForm((f) => ({
      ...f,
      steps: [...f.steps, { ...emptyStep(), order: f.steps.length + 1 }],
    }));
  };

  const removeStep = (idx) => {
    setForm((f) => {
      const steps = f.steps
        .filter((_, i) => i !== idx)
        .map((s, i) => ({ ...s, order: i + 1 }));
      return { ...f, steps: steps.length ? steps : [emptyStep()] };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError("Name is required.");
      return;
    }
    if (!form.trigger_event.trim()) {
      setError("Trigger event is required.");
      return;
    }

    setSaving(true);
    setError("");
    try {
      const payload = {
        name: form.name.trim(),
        description: form.description.trim(),
        project:
          form.project !== "" && form.project != null
            ? Number(form.project)
            : null,
        trigger_event: form.trigger_event.trim(),
        status: form.status,
        steps: form.steps
          .filter((s) => s.name.trim())
          .map((s, i) => ({
            ...(s.id ? { id: s.id } : {}),
            name: s.name.trim(),
            step_type: s.step_type,
            assignee_role: s.assignee_role.trim() || null,
            order: i + 1,
          })),
      };

      if (isEdit) {
        await workflowService.update(initial.id, payload);
      } else {
        await workflowService.create(payload);
      }
      onSaved();
      onClose();
    } catch (err) {
      setError(getApiError(err, "Failed to save workflow."));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="workflows-overlay">
      <div className="workflows-modal-panel">
        <div className="workflows-modal-header">
          <h3 className="workflows-modal-title">
            {isEdit ? "Edit Workflow" : "Create Workflow"}
          </h3>
          <button
            onClick={onClose}
            className="workflows-close-btn"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="workflows-modal-body">
          {error && (
            <div className="workflows-error">
              {error}
            </div>
          )}

          <div>
            <label className={labelCls}>Name *</label>
            <input
              className={inputCls}
              value={form.name}
              onChange={(e) => updateField("name", e.target.value)}
              placeholder="Workflow name"
              required
            />
          </div>

          <div>
            <label className={labelCls}>Description</label>
            <textarea
              className={inputCls + " min-h-[80px] resize-y"}
              value={form.description}
              onChange={(e) => updateField("description", e.target.value)}
              placeholder="What does this workflow do?"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className={labelCls}>Project ID</label>
              <input
                className={inputCls}
                type="number"
                min="1"
                value={form.project}
                onChange={(e) => updateField("project", e.target.value)}
                placeholder="Project primary key"
              />
            </div>
            <div>
              <label className={labelCls}>Status</label>
              <select
                className={inputCls}
                value={form.status}
                onChange={(e) => updateField("status", e.target.value)}
              >
                {Object.entries(WORKFLOW_STATUS).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className={labelCls}>Trigger Event *</label>
            <input
              className={inputCls}
              value={form.trigger_event}
              onChange={(e) => updateField("trigger_event", e.target.value)}
              placeholder="e.g. document.uploaded"
              required
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className={labelCls + " mb-0"}>Steps</label>
              <button
                type="button"
                onClick={addStep}
                className="workflows-add-step-btn"
              >
                <span className="material-symbols-outlined text-[16px]">add</span>
                Add step
              </button>
            </div>
            <div className="space-y-3">
              {form.steps.map((step, idx) => (
                <div
                  key={idx}
                  className="workflows-step-card"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-[11px] font-bold text-on-surface-variant">
                      Step {idx + 1}
                    </span>
                    <button
                      type="button"
                      onClick={() => removeStep(idx)}
                      className="workflows-step-remove-btn"
                    >
                      <span className="material-symbols-outlined text-[18px]">delete</span>
                    </button>
                  </div>
                  <input
                    className={inputCls}
                    value={step.name}
                    onChange={(e) => updateStep(idx, "name", e.target.value)}
                    placeholder="Step name"
                  />
                  <div className="grid grid-cols-2 gap-2">
                    <select
                      className={inputCls}
                      value={step.step_type}
                      onChange={(e) => updateStep(idx, "step_type", e.target.value)}
                    >
                      {STEP_TYPES.map((t) => (
                        <option key={t} value={t}>
                          {STEP_TYPE_LABEL[t] || t}
                        </option>
                      ))}
                    </select>
                    <input
                      className={inputCls}
                      value={step.assignee_role}
                      onChange={(e) => updateStep(idx, "assignee_role", e.target.value)}
                      placeholder="Assignee role (optional)"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </form>

        <div className="workflows-modal-footer">
          <button
            type="button"
            onClick={onClose}
            className="workflows-cancel-btn"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={saving}
            className="workflows-save-btn"
          >
            {saving ? "Saving..." : isEdit ? "Save Changes" : "Create Workflow"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Start Execution Modal → POST to Django
// ─────────────────────────────────────────────────────────────
function StartExecutionModal({ workflow, onClose, onStarted }) {
  const [entityType, setEntityType] = useState("document");
  const [entityId, setEntityId] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const handleStart = async (e) => {
    e.preventDefault();
    if (!entityId.trim()) {
      setError("Entity ID is required.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      await workflowService.startExecution(workflow.id, {
        entity_type: entityType,
        entity_id: entityId.trim(),
      });
      onStarted();
      onClose();
    } catch (err) {
      setError(getApiError(err, "Failed to start execution."));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="workflows-overlay">
      <div className="workflows-modal-panel-sm">
        <div className="workflows-modal-header">
          <h3 className="workflows-modal-title">Start Execution</h3>
          <button
            onClick={onClose}
            className="workflows-close-btn"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
        <form onSubmit={handleStart} className="workflows-modal-body-sm">
          {error && (
            <div className="workflows-error">
              {error}
            </div>
          )}
          <p className="text-sm text-on-surface-variant">
            Run <strong className="text-on-surface">{workflow.name}</strong> against an entity.
          </p>
          <div>
            <label className={labelCls}>Entity Type</label>
            <select
              className={inputCls}
              value={entityType}
              onChange={(e) => setEntityType(e.target.value)}
            >
              <option value="document">Document</option>
              <option value="project">Project</option>
              <option value="task">Task</option>
              <option value="requirement">Requirement</option>
            </select>
          </div>
          <div>
            <label className={labelCls}>Entity ID *</label>
            <input
              className={inputCls}
              value={entityId}
              onChange={(e) => setEntityId(e.target.value)}
              placeholder="Primary key of the entity"
              required
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="workflows-cancel-btn"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="workflows-save-btn"
            >
              {saving ? "Starting..." : "Start Execution"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// Workflow Detail (loads executions + history from API)
// ─────────────────────────────────────────────────────────────
function WorkflowDetail({ workflow, onBack, onChanged, onEdit }) {
  const [subTab, setSubTab] = useState("overview");
  const [executions, setExecutions] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [historyFilter, setHistoryFilter] = useState("");
  const [showStartModal, setShowStartModal] = useState(false);

  const loadData = useCallback(() => {
    setLoading(true);
    Promise.allSettled([
      workflowService.executions(workflow.id),
      workflowService.workflowHistory(workflow.id),
    ]).then(([eRes, hRes]) => {
      if (eRes.status === "fulfilled") {
        const data = eRes.value.data;
        setExecutions(Array.isArray(data) ? data : data?.results || []);
      }
      if (hRes.status === "fulfilled") {
        const data = hRes.value.data;
        setHistory(Array.isArray(data) ? data : data?.results || []);
      }
      setLoading(false);
    });
  }, [workflow.id]);

  useEffect(() => {
    loadData();
  }, [loadData]);

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
      loadData();
      onChanged();
    } catch (err) {
      alert(getApiError(err, "Failed to complete execution."));
    }
  };

  const cancelExecution = async (execution) => {
    if (!window.confirm(`Cancel execution #${execution.id}?`)) return;
    try {
      await workflowService.cancelExecution(execution.id);
      loadData();
      onChanged();
    } catch (err) {
      alert(getApiError(err, "Failed to cancel execution."));
    }
  };

  return (
    <>
      <div className="workflows-card soft-shadow">
        <div className="workflows-detail-header">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div className="flex items-start gap-3">
              <button
                onClick={onBack}
                className="workflows-close-btn"
                title="Back to workflows"
              >
                <span className="material-symbols-outlined">arrow_back</span>
              </button>
              <div>
                <h3 className="workflows-modal-title">{workflow.name}</h3>
                <p className="text-xs text-on-surface-variant mt-0.5">
                  {workflow.project_name || (workflow.project ? `Project #${workflow.project}` : "No project")} · Trigger:{" "}
                  {workflow.trigger_event}
                </p>
                {workflow.description && (
                  <p className="text-sm text-on-surface-variant mt-2">{workflow.description}</p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              {workflowBadge(workflow.status)}
              <button
                onClick={() => setShowStartModal(true)}
                className="workflows-start-btn"
              >
                <span className="material-symbols-outlined text-[16px]">play_arrow</span>
                Start Run
              </button>
              <button
                onClick={() => onEdit(workflow)}
                className="workflows-edit-btn"
              >
                <span className="material-symbols-outlined text-[16px]">edit</span>
                Edit
              </button>
              <button
                onClick={toggleStatus}
                className={`workflows-toggle-btn ${
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
                className={`workflows-tab ${
                  subTab === key
                    ? "workflows-tab-active"
                    : "workflows-tab-idle"
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
                Steps ({workflow.steps?.length || 0})
              </h4>
              {!workflow.steps?.length ? (
                <p className="text-sm text-on-surface-variant">No steps defined yet.</p>
              ) : (
                <div className="space-y-2">
                  {workflow.steps.map((step) => (
                    <div
                      key={step.id}
                      className="workflows-step-row"
                    >
                      <span className="workflows-step-num">
                        {step.order}
                      </span>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-on-surface">{step.name}</p>
                        <p className="text-[11px] text-on-surface-variant">
                          {STEP_TYPE_LABEL[step.step_type] || step.step_type}
                          {step.assignee_role ? ` · ${step.assignee_role}` : ""}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="workflows-info-card">
                  <p className="text-[11px] text-on-surface-variant uppercase tracking-wider">Status</p>
                  <p className="text-sm font-semibold text-on-surface mt-1">{workflow.status}</p>
                </div>
                <div className="workflows-info-card">
                  <p className="text-[11px] text-on-surface-variant uppercase tracking-wider">Trigger Event</p>
                  <p className="text-sm font-semibold text-on-surface mt-1 break-words">
                    {workflow.trigger_event}
                  </p>
                </div>
                <div className="workflows-info-card">
                  <p className="text-[11px] text-on-surface-variant uppercase tracking-wider">Created By</p>
                  <p className="text-sm font-semibold text-on-surface mt-1">
                    {workflow.created_by_name || "N/A"}
                  </p>
                </div>
              </div>
            </div>
          ) : subTab === "executions" ? (
            executions.length === 0 ? (
              <div className="text-center py-10">
                <span className="material-symbols-outlined text-[40px] text-outline-variant">play_circle</span>
                <p className="text-on-surface-variant mt-3 text-sm">No executions yet</p>
                <button
                  onClick={() => setShowStartModal(true)}
                  className="workflows-mini-btn"
                >
                  Start first run
                </button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="workflows-th-row">
                      <th className="workflows-th">ID</th>
                      <th className="workflows-th">Entity</th>
                      <th className="workflows-th">Status</th>
                      <th className="workflows-th">Initiated By</th>
                      <th className="workflows-th">Started</th>
                      <th className="workflows-th">Completed</th>
                      <th className="workflows-th text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {executions.map((exec) => (
                      <tr key={exec.id} className="workflows-tr">
                        <td className="workflows-td-strong">#{exec.id}</td>
                        <td className="workflows-td-muted">
                          {exec.entity_type} #{exec.entity_id}
                        </td>
                        <td className="workflows-td">{statusBadge(exec.status)}</td>
                        <td className="workflows-td-muted">
                          {exec.initiated_by_name || "—"}
                        </td>
                        <td className="workflows-td-muted text-xs">
                          {formatDate(exec.started_at)}
                        </td>
                        <td className="workflows-td-muted text-xs">
                          {formatDate(exec.completed_at)}
                        </td>
                        <td className="workflows-td text-right">
                          {exec.status === "running" && (
                            <div className="inline-flex gap-2">
                              <button
                                onClick={() => completeExecution(exec)}
                                className="workflows-complete-btn"
                              >
                                Complete
                              </button>
                              <button
                                onClick={() => cancelExecution(exec)}
                                className="workflows-cancel-sm-btn"
                              >
                                Cancel
                              </button>
                            </div>
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
                  className="workflows-filter-select"
                >
                  <option value="">All event types</option>
                  {Object.keys(HISTORY_EVENT_STYLE).map((key) => (
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

      {showStartModal && (
        <StartExecutionModal
          workflow={workflow}
          onClose={() => setShowStartModal(false)}
          onStarted={() => {
            loadData();
            onChanged();
          }}
        />
      )}
    </>
  );
}

// ─────────────────────────────────────────────────────────────
// Main Page — all data from Django via workflowService
// ─────────────────────────────────────────────────────────────
export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");
  const [formModal, setFormModal] = useState(null);

  const fetchWorkflows = useCallback(async () => {
    setLoading(true);
    const params = {};
    if (statusFilter) params.status = statusFilter;
    if (search.trim()) params.search = search.trim();
    try {
      const res = await workflowService.list(params);
      const data = res.data?.results ?? res.data ?? [];
      setWorkflows(Array.isArray(data) ? data : []);
      setSelected((prev) => (prev ? data.find((w) => w.id === prev.id) || null : prev));
    } catch (err) {
      console.error("Failed to fetch workflows:", err);
      setWorkflows([]);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, search]);

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
      <TopHeader title="Workflows" subtitle="Automation flows and execution history" />

      {selected ? (
        <WorkflowDetail
          workflow={selected}
          onBack={() => setSelected(null)}
          onChanged={fetchWorkflows}
          onEdit={(wf) => setFormModal(wf)}
        />
      ) : (
        <>
          <div className="workflows-toolbar soft-shadow">
            <div>
              <h3 className="workflows-h3">All Workflows</h3>
              <p className="text-xs text-on-surface-variant mt-0.5">
                Data loaded from the database. Select a workflow to view steps, executions and history.
              </p>
            </div>
            <div className="flex items-center gap-2 flex-wrap">
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[18px] text-on-surface-variant">
                  search
                </span>
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search workflows..."
                  className="workflows-search-input"
                />
              </div>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="workflows-select"
              >
                <option value="">All statuses</option>
                {Object.entries(WORKFLOW_STATUS).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v.label}
                  </option>
                ))}
              </select>
              <button
                onClick={() => setFormModal("create")}
                className="workflows-new-btn"
              >
                <span className="material-symbols-outlined text-[16px]">add</span>
                New Workflow
              </button>
            </div>
          </div>

          {loading ? (
            <div className="workflows-card soft-shadow p-6">
              <p className="text-sm text-on-surface-variant">Loading workflows...</p>
            </div>
          ) : workflows.length === 0 ? (
            <div className="workflows-empty-card soft-shadow">
              <span className="material-symbols-outlined text-[48px] text-outline-variant">
                account_tree
              </span>
              <p className="text-on-surface-variant mt-3 text-sm">No workflows in the database</p>
              <button
                onClick={() => setFormModal("create")}
                className="workflows-mini-btn"
              >
                Create your first workflow
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {workflows.map((workflow) => (
                <div
                  key={workflow.id}
                  className="workflows-wf-card soft-shadow"
                  onClick={() => setSelected(workflow)}
                >
                  <div className="flex items-start justify-between mb-3">
                    {workflowBadge(workflow.status)}
                    <div className="flex items-center gap-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setFormModal(workflow);
                        }}
                        className="workflows-icon-btn"
                        title="Edit"
                      >
                        <span className="material-symbols-outlined text-[18px]">edit</span>
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteWorkflow(workflow);
                        }}
                        className="workflows-icon-btn hover:text-red-500"
                        title="Delete"
                      >
                        <span className="material-symbols-outlined text-[18px]">delete</span>
                      </button>
                    </div>
                  </div>
                  <h4 className="workflows-h3">{workflow.name}</h4>
                  <p className="text-xs text-on-surface-variant mt-1 flex-1">
                    {workflow.description || "No description"}
                  </p>
                  <div className="workflows-card-footer">
                    <span className="inline-flex items-center gap-1">
                      <span className="material-symbols-outlined text-[14px]">steps</span>
                      {workflow.steps?.length || 0} steps
                    </span>
                    <span className="inline-flex items-center gap-1">
                      <span className="material-symbols-outlined text-[14px]">history</span>
                      {workflow.execution_count ?? 0} runs
                    </span>
                    <span className="inline-flex items-center gap-1 truncate max-w-[100px]">
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

      {formModal && (
        <WorkflowFormModal
          initial={formModal === "create" ? null : formModal}
          onClose={() => setFormModal(null)}
          onSaved={fetchWorkflows}
        />
      )}
    </div>
  );
}
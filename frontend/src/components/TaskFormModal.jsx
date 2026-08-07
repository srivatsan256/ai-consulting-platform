import React, { useState, useEffect } from "react";

const STATUS_OPTIONS = [
  { value: "todo", label: "To Do" },
  { value: "in_progress", label: "In Progress" },
  { value: "blocked", label: "Blocked" },
  { value: "review", label: "Review" },
  { value: "done", label: "Done" },
];

const PRIORITY_OPTIONS = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
  { value: "critical", label: "Critical" },
];

export default function TaskFormModal({ open, onClose, onSubmit, submitting, form, setForm, formError }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[100] p-4">
      <div className="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto soft-shadow">
        <div className="p-6 border-b border-outline-variant/20 flex items-center justify-between">
          <h3 className="font-headline-lg text-lg font-bold text-on-surface">
            {form.id ? "Edit Task" : "New Task"}
          </h3>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-surface-container transition-colors"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit();
          }}
          className="p-6 space-y-4"
        >
          {formError && (
            <div className="flex items-start gap-2 px-4 py-3 rounded-xl bg-error/10 border border-error/30 text-on-surface text-sm">
              <span className="material-symbols-outlined text-[18px] text-error shrink-0">error</span>
              <span>{formError}</span>
            </div>
          )}
          <div>
            <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">
              Title *
            </label>
            <input
              type="text"
              required
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="e.g. Design the data model"
              className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
            />
          </div>
          <div>
            <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">
              Description
            </label>
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Describe the task..."
              rows={3}
              className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 resize-none"
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">
                Project *
              </label>
              <select
                required
                value={form.project || ""}
                onChange={(e) => setForm({ ...form, project: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
              >
                <option value="">Select project</option>
                {form.projectOptions.map((p) => (
                  <option key={p.id} value={p.id}>{p.project_name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">
                Assignee
              </label>
              <select
                value={form.assigned_to || ""}
                onChange={(e) => setForm({ ...form, assigned_to: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
              >
                <option value="">Unassigned</option>
                {form.userOptions.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.full_name || u.username || u.email}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">
                Status
              </label>
              <select
                value={form.status}
                onChange={(e) => setForm({ ...form, status: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
              >
                {STATUS_OPTIONS.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">
                Priority
              </label>
              <select
                value={form.priority}
                onChange={(e) => setForm({ ...form, priority: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
              >
                {PRIORITY_OPTIONS.map((p) => (
                  <option key={p.value} value={p.value}>{p.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">
                Start Date
              </label>
              <input
                type="date"
                value={form.start_date || ""}
                onChange={(e) => setForm({ ...form, start_date: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">
                Due Date
              </label>
              <input
                type="date"
                value={form.due_date || ""}
                onChange={(e) => setForm({ ...form, due_date: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="block font-label-md text-[11px] uppercase tracking-wider text-on-surface-variant mb-1.5">
                Estimated Hours
              </label>
              <input
                type="number"
                step="0.5"
                min="0"
                value={form.estimated_hours ?? ""}
                onChange={(e) => setForm({ ...form, estimated_hours: e.target.value })}
                placeholder="e.g. 8"
                className="w-full px-4 py-2.5 rounded-xl border border-outline-variant/40 bg-surface-container-low text-on-surface text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
              />
            </div>
          </div>
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 rounded-xl border border-outline-variant/40 text-on-surface-variant text-sm font-medium hover:bg-surface-container transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 py-2.5 rounded-xl bg-primary text-on-primary text-sm font-bold hover:opacity-90 transition-all disabled:opacity-50"
            >
              {submitting ? "Saving..." : form.id ? "Update Task" : "Create Task"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

import React, { useState, useEffect } from "react";
import "../styles/components/TaskFormModal.css";

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
    <div className="taskform-overlay">
      <div className="taskform-panel soft-shadow">
        <div className="taskform-header">
          <h3 className="taskform-title">
            {form.id ? "Edit Task" : "New Task"}
          </h3>
          <button
            onClick={onClose}
            className="taskform-close"
          >
            <span className="material-symbols-outlined taskform-close-icon">close</span>
          </button>
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit();
          }}
          className="taskform-form"
        >
          {formError && (
            <div className="taskform-error">
              <span className="material-symbols-outlined taskform-error-icon">error</span>
              <span>{formError}</span>
            </div>
          )}
          <div>
            <label className="taskform-label">
              Title *
            </label>
            <input
              type="text"
              required
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="e.g. Design the data model"
              className="taskform-input"
            />
          </div>
          <div>
            <label className="taskform-label">
              Description
            </label>
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Describe the task..."
              rows={3}
              className="taskform-textarea"
            />
          </div>
          <div className="taskform-grid">
            <div>
              <label className="taskform-label">
                Project *
              </label>
              <select
                required
                value={form.project || ""}
                onChange={(e) => setForm({ ...form, project: e.target.value })}
                className="taskform-select"
              >
                <option value="">Select project</option>
                {form.projectOptions.map((p) => (
                  <option key={p.id} value={p.id}>{p.project_name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="taskform-label">
                Assignee
              </label>
              <select
                value={form.assigned_to || ""}
                onChange={(e) => setForm({ ...form, assigned_to: e.target.value })}
                className="taskform-select"
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
              <label className="taskform-label">
                Status
              </label>
              <select
                value={form.status}
                onChange={(e) => setForm({ ...form, status: e.target.value })}
                className="taskform-select"
              >
                {STATUS_OPTIONS.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="taskform-label">
                Priority
              </label>
              <select
                value={form.priority}
                onChange={(e) => setForm({ ...form, priority: e.target.value })}
                className="taskform-select"
              >
                {PRIORITY_OPTIONS.map((p) => (
                  <option key={p.value} value={p.value}>{p.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="taskform-label">
                Start Date
              </label>
              <input
                type="date"
                value={form.start_date || ""}
                onChange={(e) => setForm({ ...form, start_date: e.target.value })}
                className="taskform-select"
              />
            </div>
            <div>
              <label className="taskform-label">
                Due Date
              </label>
              <input
                type="date"
                value={form.due_date || ""}
                onChange={(e) => setForm({ ...form, due_date: e.target.value })}
                className="taskform-select"
              />
            </div>
            <div>
              <label className="taskform-label">
                Estimated Hours
              </label>
              <input
                type="number"
                step="0.5"
                min="0"
                value={form.estimated_hours ?? ""}
                onChange={(e) => setForm({ ...form, estimated_hours: e.target.value })}
                placeholder="e.g. 8"
                className="taskform-input"
              />
            </div>
          </div>
          <div className="taskform-actions">
            <button
              type="button"
              onClick={onClose}
              className="taskform-cancel"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="taskform-submit"
            >
              {submitting ? "Saving..." : form.id ? "Update Task" : "Create Task"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

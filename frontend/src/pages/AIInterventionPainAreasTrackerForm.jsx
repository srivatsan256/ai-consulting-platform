import React, { useState, useEffect } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import TopHeader from "../components/TopHeader";
import { painAreaService } from "../services/api";
import "../styles/pages/AIInterventionPainAreasTracker.css";

const PRIORITY_OPTIONS = ["High", "Medium", "Low"];
const FEASIBILITY_OPTIONS = ["High", "Medium", "Low"];
const STATUS_OPTIONS = ["Open", "In Progress", "Completed", "On Hold", "Cancelled"];

const EMPTY_FORM = {
  date: new Date().toISOString().split("T")[0],
  department: "",
  process_activity: "",
  pain_area: "",
  current_method: "",
  frequency: "",
  time_spent_hrs: "",
  impact_area: "",
  ai_intervention: "",
  expected_benefit: "",
  priority: "Medium",
  feasibility: "Medium",
  owner: "",
  target_date: "",
  status: "Open",
  remarks: "",
};

export default function AIInterventionPainAreasTrackerForm() {
  const navigate = useNavigate();
  const { id } = useParams();
  const location = useLocation();
  const editId = id || null;

  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(!!editId);

  const goBack = () => navigate("/ai-pain-areas");

  // --------------------------------------------------
  // Pre-fill form when editing
  // --------------------------------------------------
  useEffect(() => {
    if (!editId) {
      setForm(EMPTY_FORM);
      return;
    }

    const initialRecord = location.state?.record;
    if (initialRecord) {
      setForm({
        date: initialRecord.date || "",
        department: initialRecord.department || "",
        process_activity: initialRecord.process_activity || "",
        pain_area: initialRecord.pain_area || "",
        current_method: initialRecord.current_method || "",
        frequency: initialRecord.frequency || "",
        time_spent_hrs: initialRecord.time_spent_hrs ?? "",
        impact_area: initialRecord.impact_area || "",
        ai_intervention: initialRecord.ai_intervention || "",
        expected_benefit: initialRecord.expected_benefit || "",
        priority: initialRecord.priority || "Medium",
        feasibility: initialRecord.feasibility || "Medium",
        owner: initialRecord.owner || "",
        target_date: initialRecord.target_date || "",
        status: initialRecord.status || "Open",
        remarks: initialRecord.remarks || "",
      });
      setLoading(false);
      return;
    }

    (async () => {
      try {
        const res = await painAreaService.list();
        const records = res.data.results || res.data || [];
        const record = records.find((r) => String(r.id) === String(editId));
        if (record) {
          setForm({
            date: record.date || "",
            department: record.department || "",
            process_activity: record.process_activity || "",
            pain_area: record.pain_area || "",
            current_method: record.current_method || "",
            frequency: record.frequency || "",
            time_spent_hrs: record.time_spent_hrs ?? "",
            impact_area: record.impact_area || "",
            ai_intervention: record.ai_intervention || "",
            expected_benefit: record.expected_benefit || "",
            priority: record.priority || "Medium",
            feasibility: record.feasibility || "Medium",
            owner: record.owner || "",
            target_date: record.target_date || "",
            status: record.status || "Open",
            remarks: record.remarks || "",
          });
        }
      } catch (err) {
        console.error("Failed to load record for edit:", err);
        alert("Failed to load record. Returning to records list.");
        goBack();
      } finally {
        setLoading(false);
      }
    })();
  }, [editId]); // eslint-disable-line react-hooks/exhaustive-deps

  // --------------------------------------------------
  // Form handlers
  // --------------------------------------------------
  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      const payload = {
        ...form,
        date: form.date || new Date().toISOString().split("T")[0],
        time_spent_hrs: form.time_spent_hrs ? Number(form.time_spent_hrs) : null,
        target_date: form.target_date || null,
      };

      if (editId) {
        await painAreaService.update(editId, payload);
      } else {
        await painAreaService.create(payload);
      }

      goBack();
    } catch (err) {
      console.error("Save error:", err);
      alert("Failed to save record. Check console for details.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <TopHeader
        title={editId ? "Edit Pain Area Record" : "New Pain Area Record"}
        subtitle="AI Intervention Pain Areas Tracker"
        actions={
          <button onClick={goBack} className="pain-secondary-btn">
            <span className="material-symbols-outlined text-[18px]">arrow_back</span>
            Back to Records
          </button>
        }
      />

      <div className="pain-panel soft-shadow">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Department */}
              <div>
                <label className="pain-label">Department</label>
                <input
                  type="text"
                  name="department"
                  value={form.department}
                  onChange={handleChange}
                  className="pain-input"
                  placeholder="e.g. Operations, Finance"
                />
              </div>

              {/* Process / Activity */}
              <div>
                <label className="pain-label">Process / Activity</label>
                <input
                  type="text"
                  name="process_activity"
                  value={form.process_activity}
                  onChange={handleChange}
                  className="pain-input"
                  placeholder="e.g. Invoice Processing"
                />
              </div>

              {/* Frequency */}
              <div>
                <label className="pain-label">Frequency</label>
                <input
                  type="text"
                  name="frequency"
                  value={form.frequency}
                  onChange={handleChange}
                  className="pain-input"
                  placeholder="e.g. Daily, Weekly"
                />
              </div>

              {/* Time Spent */}
              <div>
                <label className="pain-label">Time Spent / Month (Hrs)</label>
                <input
                  type="number"
                  step="0.5"
                  name="time_spent_hrs"
                  value={form.time_spent_hrs}
                  onChange={handleChange}
                  className="pain-input"
                  placeholder="e.g. 40"
                />
              </div>

              {/* Impact Area */}
              <div>
                <label className="pain-label">Impact Area</label>
                <input
                  type="text"
                  name="impact_area"
                  value={form.impact_area}
                  onChange={handleChange}
                  className="pain-input"
                  placeholder="e.g. Cost, Quality, Speed"
                />
              </div>

              {/* Priority */}
              <div>
                <label className="pain-label">Priority</label>
                <select
                  name="priority"
                  value={form.priority}
                  onChange={handleChange}
                  className="pain-input"
                >
                  {PRIORITY_OPTIONS.map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>

              {/* Feasibility */}
              <div>
                <label className="pain-label">Feasibility</label>
                <select
                  name="feasibility"
                  value={form.feasibility}
                  onChange={handleChange}
                  className="pain-input"
                >
                  {FEASIBILITY_OPTIONS.map((f) => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>
              </div>

              {/* Owner */}
              <div>
                <label className="pain-label">Owner</label>
                <input
                  type="text"
                  name="owner"
                  value={form.owner}
                  onChange={handleChange}
                  className="pain-input"
                  placeholder="Responsible person"
                />
              </div>

              {/* Target Date */}
              <div>
                <label className="pain-label">Target Date</label>
                <input
                  type="date"
                  name="target_date"
                  value={form.target_date}
                  onChange={handleChange}
                  className="pain-input"
                />
              </div>

              {/* Status */}
              <div>
                <label className="pain-label">Status</label>
                <select
                  name="status"
                  value={form.status}
                  onChange={handleChange}
                  className="pain-input"
                >
                  {STATUS_OPTIONS.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Full width fields */}
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="pain-label">Pain Area / Problem Statement</label>
                <textarea
                  name="pain_area"
                  value={form.pain_area}
                  onChange={handleChange}
                  className="pain-textarea"
                  rows={2}
                  placeholder="Describe the pain point..."
                />
              </div>

              <div>
                <label className="pain-label">Current Method</label>
                <textarea
                  name="current_method"
                  value={form.current_method}
                  onChange={handleChange}
                  className="pain-textarea"
                  rows={2}
                  placeholder="How is it currently handled?"
                />
              </div>

              <div>
                <label className="pain-label">AI Intervention Required</label>
                <textarea
                  name="ai_intervention"
                  value={form.ai_intervention}
                  onChange={handleChange}
                  className="pain-textarea"
                  rows={2}
                  placeholder="What AI solution is needed?"
                />
              </div>

              <div>
                <label className="pain-label">Expected Benefit</label>
                <textarea
                  name="expected_benefit"
                  value={form.expected_benefit}
                  onChange={handleChange}
                  className="pain-textarea"
                  rows={2}
                  placeholder="Expected impact / ROI"
                />
              </div>

              <div>
                <label className="pain-label">Remarks</label>
                <textarea
                  name="remarks"
                  value={form.remarks}
                  onChange={handleChange}
                  className="pain-textarea"
                  rows={2}
                  placeholder="Any additional notes..."
                />
              </div>
            </div>

            <div className="flex items-center gap-3 pt-2">
              <button
                type="submit"
                disabled={saving}
                className="pain-primary-btn"
              >
                {saving ? (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <span className="material-symbols-outlined text-[18px]">
                    {editId ? "save" : "add"}
                  </span>
                )}
                {saving ? "Saving..." : editId ? "Update Record" : "Add Record"}
              </button>

              <button
                type="button"
                onClick={goBack}
                className="pain-secondary-btn"
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

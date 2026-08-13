import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import TopHeader from "../components/TopHeader";
import { painAreaService, getApiError } from "../services/api";
import "../styles/pages/AIInterventionPainAreasTracker.css";

const PRIORITY_OPTIONS = ["High", "Medium", "Low"];
const STATUS_OPTIONS = ["Open", "In Progress", "Completed", "On Hold", "Cancelled"];

export default function AIInterventionPainAreasTrackerRecord() {
  const navigate = useNavigate();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState("All");
  const [filterPriority, setFilterPriority] = useState("All");

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const res = await painAreaService.list();
      setRecords(res.data.results || res.data || []);
    } catch (err) {
      console.error("Failed to fetch records:", err);
      setRecords([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this record?")) return;

    try {
      await painAreaService.remove(id);
      await fetchRecords();
    } catch (err) {
      console.error("Delete error:", err);
      await fetchRecords();
      alert(getApiError(err, "Failed to delete record."));
    }
  };

  const filteredRecords = records.filter((r) => {
    const statusMatch = filterStatus === "All" || r.status === filterStatus;
    const priorityMatch = filterPriority === "All" || r.priority === filterPriority;
    return statusMatch && priorityMatch;
  });

  const getPriorityClass = (priority) => {
    if (priority === "High") return "bg-red-100 text-red-700";
    if (priority === "Medium") return "bg-amber-100 text-amber-700";
    return "bg-emerald-100 text-emerald-700";
  };

  const getStatusClass = (status) => {
    const map = {
      Open: "bg-blue-100 text-blue-700",
      "In Progress": "bg-purple-100 text-purple-700",
      Completed: "bg-emerald-100 text-emerald-700",
      "On Hold": "bg-amber-100 text-amber-700",
      Cancelled: "bg-gray-100 text-gray-600",
    };
    return map[status] || "bg-gray-100 text-gray-600";
  };

  return (
    <div className="space-y-6">
      <TopHeader
        title="AI Intervention Pain Areas Tracker"
        subtitle="Track process pain points and AI intervention opportunities"
        actions={
          <button
            onClick={() => navigate("/ai-pain-areas/new")}
            className="pain-primary-btn"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            Add New Record
          </button>
        }
      />

      {/* Filters */}
      <div className="pain-filters soft-shadow">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <span className="text-xs text-on-surface-variant font-medium">Status:</span>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="pain-select"
            >
              <option value="All">All</option>
              {STATUS_OPTIONS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-on-surface-variant font-medium">Priority:</span>
            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="pain-select"
            >
              <option value="All">All</option>
              {PRIORITY_OPTIONS.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>

          <div className="ml-auto text-xs text-on-surface-variant">
            Showing <span className="font-bold text-on-surface">{filteredRecords.length}</span> of{" "}
            <span className="font-bold text-on-surface">{records.length}</span> records
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="pain-panel soft-shadow">
        <div className="flex items-center justify-between mb-4">
          <h3 className="pain-h3">Records</h3>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          </div>
        ) : filteredRecords.length === 0 ? (
          <div className="text-center py-16">
            <span className="material-symbols-outlined text-[48px] text-outline-variant">
              table_chart
            </span>
            <p className="text-on-surface-variant mt-3 text-sm">
              No records found. Click “Add New Record” to get started.
            </p>
          </div>
        ) : (
          <div className="pain-table-wrap">
            <table className="w-full text-sm">
              <thead>
                <tr className="pain-table-head-row">
                  <th className="pain-th">#</th>
                  <th className="pain-th">Date</th>
                  <th className="pain-th">Department</th>
                  <th className="pain-th">Process / Activity</th>
                  <th className="pain-th">Pain Area</th>
                  <th className="pain-th">Priority</th>
                  <th className="pain-th">Status</th>
                  <th className="pain-th">Owner</th>
                  <th className="pain-th">Target Date</th>
                  <th className="pain-th text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredRecords.map((record, index) => (
                  <tr key={record.id} className="pain-row">
                    <td className="pain-td text-on-surface-variant">{index + 1}</td>
                    <td className="pain-td whitespace-nowrap">
                      {record.date ? new Date(record.date).toLocaleDateString() : "—"}
                    </td>
                    <td className="pain-td">{record.department || "—"}</td>
                    <td className="pain-td max-w-[180px]">
                      <p className="truncate" title={record.process_activity}>
                        {record.process_activity || "—"}
                      </p>
                    </td>
                    <td className="pain-td max-w-[220px]">
                      <p className="truncate" title={record.pain_area}>
                        {record.pain_area || "—"}
                      </p>
                    </td>
                    <td className="pain-td">
                      <span className={`pain-pill ${getPriorityClass(record.priority)}`}>
                        {record.priority || "—"}
                      </span>
                    </td>
                    <td className="pain-td">
                      <span className={`pain-pill ${getStatusClass(record.status)}`}>
                        {record.status || "—"}
                      </span>
                    </td>
                    <td className="pain-td">{record.owner || "—"}</td>
                    <td className="pain-td whitespace-nowrap">
                      {record.target_date
                        ? new Date(record.target_date).toLocaleDateString()
                        : "—"}
                    </td>
                    <td className="pain-td">
                      <div className="flex items-center justify-center gap-1">
                        <button
                          onClick={() => navigate(`/ai-pain-areas/${record.id}/edit`, { state: { record } })}
                          className="pain-action-btn"
                          title="Edit"
                        >
                          <span className="material-symbols-outlined text-[18px]">edit</span>
                        </button>
                        <button
                          onClick={() => handleDelete(record.id)}
                          className="pain-action-btn text-red-600 hover:bg-red-50"
                          title="Delete"
                        >
                          <span className="material-symbols-outlined text-[18px]">delete</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

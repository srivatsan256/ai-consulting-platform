import React, { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Label,
} from "recharts";
import TopHeader from "../components/TopHeader";
import CsvUploadFlow from "../components/CsvUploadFlow/CsvUploadFlow";
import { painAreaService, getApiError } from "../services/api";
import "../styles/pages/AIInterventionPainAreasTrackerRecord.css";

const PRIORITY_OPTIONS = ["High", "Medium", "Low"];
const STATUS_OPTIONS = ["Open", "In Progress", "Completed", "On Hold", "Cancelled"];
const CHART_COLORS = {
  High: "#DC2626",
  Medium: "#D97706",
  Low: "#059669",
  Open: "#64748B",
  "In Progress": "#2563EB",
  Completed: "#16A34A",
  "On Hold": "#EA580C",
  Cancelled: "#94A3B8",
  default: ["#0D9488", "#4F46E5", "#F59E0B", "#F43F5E", "#10B981", "#8B5CF6", "#0EA5E9", "#64748B"],
};

export default function AIInterventionPainAreasTrackerRecord() {
  const navigate = useNavigate();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState("All");
  const [filterPriority, setFilterPriority] = useState("All");
  const [filterDepartment, setFilterDepartment] = useState("All");
  const [isUploadFlowOpen, setUploadFlowOpen] = useState(false);
  const [lastImport, setLastImport] = useState(null);

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

  const filteredRecords = useMemo(() => {
    return records.filter((r) => {
      const statusMatch = filterStatus === "All" || r.status === filterStatus;
      const priorityMatch = filterPriority === "All" || r.priority === filterPriority;
      const deptMatch = filterDepartment === "All" || r.department === filterDepartment;
      return statusMatch && priorityMatch && deptMatch;
    });
  }, [records, filterStatus, filterPriority, filterDepartment]);

  const departments = useMemo(() => {
    const set = new Set(records.map((r) => r.department).filter(Boolean));
    return Array.from(set).sort();
  }, [records]);

  const kpis = useMemo(() => {
    const total = filteredRecords.length;
    const highPriority = filteredRecords.filter((r) => r.priority === "High").length;
    const completed = filteredRecords.filter((r) => r.status === "Completed").length;
    const onTrack = filteredRecords.filter((r) => {
      if (r.status === "Completed" || r.status === "Cancelled") return true;
      if (!r.target_date) return false;
      return new Date(r.target_date) >= new Date();
    }).length;
    const totalHours = filteredRecords.reduce((sum, r) => {
      return sum + (Number(r.time_spent_hrs) || 0);
    }, 0);
    const potentialSave = filteredRecords.reduce((sum, r) => {
      const hours = Number(r.time_spent_hrs) || 0;
      const hasAI = r.ai_intervention && String(r.ai_intervention).trim().length > 0;
      return sum + (hasAI ? hours : 0);
    }, 0);
    return {
      total,
      highPriority,
      highPriorityPct: total ? Math.round((highPriority / total) * 100) : 0,
      completed,
      completedPct: total ? Math.round((completed / total) * 100) : 0,
      onTrackPct: total ? Math.round((onTrack / total) * 100) : 0,
      totalHours: Math.round(totalHours),
      potentialSave: Math.round(potentialSave),
    };
  }, [filteredRecords]);

  const statusPieData = useMemo(() => {
    const counts = {};
    filteredRecords.forEach((r) => {
      const s = r.status || "Unknown";
      counts[s] = (counts[s] || 0) + 1;
    });
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [filteredRecords]);

  const priorityPieData = useMemo(() => {
    const counts = { High: 0, Medium: 0, Low: 0 };
    filteredRecords.forEach((r) => {
      if (counts[r.priority] !== undefined) counts[r.priority]++;
    });
    return Object.entries(counts)
      .filter(([, v]) => v > 0)
      .map(([name, value]) => ({ name, value }));
  }, [filteredRecords]);

  const departmentBarData = useMemo(() => {
    const map = {};
    filteredRecords.forEach((r) => {
      const dept = r.department || "Unknown";
      const hours = Number(r.time_spent_hrs) || 0;
      if (!map[dept]) map[dept] = { department: dept, hours: 0, count: 0 };
      map[dept].hours += hours;
      map[dept].count += 1;
    });
    return Object.values(map)
      .sort((a, b) => b.hours - a.hours)
      .slice(0, 8);
  }, [filteredRecords]);

  const priorityStatusBarData = useMemo(() => {
    const priorities = ["High", "Medium", "Low"];
    return priorities.map((p) => {
      const row = { priority: p };
      STATUS_OPTIONS.forEach((s) => {
        row[s] = filteredRecords.filter((r) => r.priority === p && r.status === s).length;
      });
      return row;
    });
  }, [filteredRecords]);

  const getPriorityClass = (priority) => {
    if (priority === "High") return "bg-red-100 text-red-700";
    if (priority === "Medium") return "bg-amber-100 text-amber-700";
    return "bg-emerald-100 text-emerald-700";
  };

  const getStatusClass = (status) => {
    const map = {
      Open: "bg-slate-100 text-slate-700",
      "In Progress": "bg-blue-100 text-blue-700",
      Completed: "bg-emerald-100 text-emerald-700",
      "On Hold": "bg-amber-100 text-amber-700",
      Cancelled: "bg-gray-100 text-gray-600",
    };
    return map[status] || "bg-gray-100 text-gray-600";
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip">
          <p className="chart-tooltip-label">{label}</p>
          {payload.map((entry, i) => (
            <p key={i} style={{ color: entry.color }}>
              {entry.name}: <strong>{entry.value}</strong>
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="pain-page">
      <TopHeader
        title="AI Intervention Pain Areas Tracker"
        subtitle="Modern dashboard · Process pain points & AI intervention opportunities"
        actions={
          <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
            <button
              onClick={() => setUploadFlowOpen(true)}
              className="pain-secondary-btn"
              style={{
                display: "inline-flex",
                flexDirection: "column",
                alignItems: "flex-start",
                gap: "2px",
                padding: "8px 14px",
                border: "1px solid #CBD5E1",
                borderRadius: "6px",
                background: "#FFFFFF",
                color: "#334155",
                fontWeight: 500,
                cursor: "pointer",
                lineHeight: 1.25,
              }}
            >
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                <span className="material-symbols-outlined text-[18px]">upload_file</span>
                Upload Using CSV
              </span>
              {lastImport && (
                <span className="pain-import-summary">
                  {lastImport.inserted} imported
                  {lastImport.skipped ? ` · ${lastImport.skipped} skipped` : ""}
                  {lastImport.warnings?.length
                    ? ` · ${lastImport.warnings.length} warning${lastImport.warnings.length === 1 ? "" : "s"}`
                    : ""}
                </span>
              )}
            </button>
            <button
              onClick={() => navigate("/ai-pain-areas/new")}
              className="pain-primary-btn"
            >
              <span className="material-symbols-outlined text-[18px]">add</span>
              Add New Record
            </button>
          </div>
        }
      />

      {/* CSV Upload Wizard Modal */}
      <CsvUploadFlow
        isOpen={isUploadFlowOpen}
        onClose={() => setUploadFlowOpen(false)}
        onComplete={(response) => {
          fetchRecords();
          const data = response?.data ?? response ?? {};
          setLastImport({
            inserted: data.inserted ?? 0,
            skipped: data.skipped ?? 0,
            warnings: data.warnings ?? [],
          });
        }}
      />

      {/* Filters */}
      <div className="pain-filters soft-shadow">
        <div className="pain-filters-inner">
          <div className="pain-filter-group">
            <span className="pain-filter-label">Status</span>
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
          <div className="pain-filter-group">
            <span className="pain-filter-label">Priority</span>
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
          <div className="pain-filter-group">
            <span className="pain-filter-label">Department</span>
            <select
              value={filterDepartment}
              onChange={(e) => setFilterDepartment(e.target.value)}
              className="pain-select"
            >
              <option value="All">All</option>
              {departments.map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>
          <div className="pain-filter-count">
            Showing <strong>{filteredRecords.length}</strong> of <strong>{records.length}</strong> records
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="pain-kpi-grid">
        <div className="pain-kpi-card soft-shadow">
          <p className="pain-kpi-label">Total Opportunities</p>
          <p className="pain-kpi-value">{kpis.total}</p>
          <p className="pain-kpi-sub">Active portfolio</p>
        </div>
        <div className="pain-kpi-card soft-shadow">
          <p className="pain-kpi-label">Total Hours / Month</p>
          <p className="pain-kpi-value">{kpis.totalHours}</p>
          <p className="pain-kpi-sub teal">Potential save: {kpis.potentialSave} hrs</p>
        </div>
        <div className="pain-kpi-card soft-shadow border-left-red">
          <p className="pain-kpi-label">High Priority</p>
          <p className="pain-kpi-value red">{kpis.highPriority}</p>
          <p className="pain-kpi-sub">{kpis.highPriorityPct}% of total</p>
        </div>
        <div className="pain-kpi-card soft-shadow">
          <p className="pain-kpi-label">Completed</p>
          <p className="pain-kpi-value green">{kpis.completed}</p>
          <p className="pain-kpi-sub">{kpis.completedPct}% done</p>
        </div>
        <div className="pain-kpi-card soft-shadow">
          <p className="pain-kpi-label">On Track</p>
          <p className="pain-kpi-value">{kpis.onTrackPct}%</p>
          <p className="pain-kpi-sub">vs Target Date</p>
        </div>
        <div className="pain-kpi-card soft-shadow">
          <p className="pain-kpi-label">AI Coverage</p>
          <p className="pain-kpi-value indigo">
            {kpis.totalHours ? Math.round((kpis.potentialSave / kpis.totalHours) * 100) : 0}%
          </p>
          <p className="pain-kpi-sub">Hours with AI planned</p>
        </div>
      </div>

      {/* Charts Row 1 - Pies */}
      <div className="pain-charts-grid">
        <div className="pain-panel soft-shadow">
          <h3 className="pain-h3">Status Distribution</h3>
          {statusPieData.length === 0 ? (
            <div className="pain-chart-empty">No data</div>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={statusPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={70}
                  outerRadius={100}
                  paddingAngle={3}
                  dataKey="value"
                  nameKey="name"
                >
                  {statusPieData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={CHART_COLORS[entry.name] || CHART_COLORS.default[index % CHART_COLORS.default.length]}
                    />
                  ))}
                  <Label value={`${kpis.total}`} position="center" className="pie-center-label" />
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend verticalAlign="bottom" height={36} iconType="circle" />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
        <div className="pain-panel soft-shadow">
          <h3 className="pain-h3">Priority Breakdown</h3>
          {priorityPieData.length === 0 ? (
            <div className="pain-chart-empty">No data</div>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={priorityPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={70}
                  outerRadius={100}
                  paddingAngle={3}
                  dataKey="value"
                  nameKey="name"
                >
                  {priorityPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CHART_COLORS[entry.name]} />
                  ))}
                  <Label value={`${kpis.total}`} position="center" className="pie-center-label" />
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend verticalAlign="bottom" height={36} iconType="circle" />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Charts Row 2 - Bars */}
      <div className="pain-charts-grid">
        <div className="pain-panel soft-shadow">
          <h3 className="pain-h3">Time Spent (Hrs/Month) by Department</h3>
          {departmentBarData.length === 0 ? (
            <div className="pain-chart-empty">No data</div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={departmentBarData} layout="vertical" margin={{ left: 20, right: 30 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                <XAxis type="number" tick={{ fontSize: 12 }} />
                <YAxis type="category" dataKey="department" width={110} tick={{ fontSize: 12 }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="hours" name="Hours" fill="#0D9488" radius={[0, 6, 6, 0]} barSize={18} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
        <div className="pain-panel soft-shadow">
          <h3 className="pain-h3">Count by Priority × Status</h3>
          {priorityStatusBarData.every((d) => STATUS_OPTIONS.every((s) => d[s] === 0)) ? (
            <div className="pain-chart-empty">No data</div>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={priorityStatusBarData} margin={{ left: 10, right: 10 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="priority" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip content={<CustomTooltip />} />
                <Legend iconType="circle" />
                {STATUS_OPTIONS.map((status) => (
                  <Bar key={status} dataKey={status} stackId="a" fill={CHART_COLORS[status]} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="pain-panel soft-shadow">
        <div className="pain-table-header">
          <h3 className="pain-h3">Records</h3>
        </div>
        {loading ? (
          <div className="pain-loading">
            <div className="pain-spinner" />
          </div>
        ) : filteredRecords.length === 0 ? (
          <div className="pain-empty">
            <span className="material-symbols-outlined pain-empty-icon">table_chart</span>
            <p>No records found. Click “Add New Record” to get started.</p>
          </div>
        ) : (
          <div className="pain-table-wrap">
            <table className="pain-table">
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
                    <td className="pain-td muted">{index + 1}</td>
                    <td className="pain-td nowrap">
                      {record.date ? new Date(record.date).toLocaleDateString() : "—"}
                    </td>
                    <td className="pain-td">{record.department || "—"}</td>
                    <td className="pain-td max-180">
                      <p className="truncate" title={record.process_activity}>
                        {record.process_activity || "—"}
                      </p>
                    </td>
                    <td className="pain-td max-220">
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
                    <td className="pain-td nowrap">
                      {record.target_date
                        ? new Date(record.target_date).toLocaleDateString()
                        : "—"}
                    </td>
                    <td className="pain-td">
                      <div className="pain-actions">
                        <button
                          onClick={() =>
                            navigate(`/ai-pain-areas/${record.id}/edit`, { state: { record } })
                          }
                          className="pain-action-btn"
                          title="Edit"
                        >
                          <span className="material-symbols-outlined">edit</span>
                        </button>
                        <button
                          onClick={() => handleDelete(record.id)}
                          className="pain-action-btn danger"
                          title="Delete"
                        >
                          <span className="material-symbols-outlined">delete</span>
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
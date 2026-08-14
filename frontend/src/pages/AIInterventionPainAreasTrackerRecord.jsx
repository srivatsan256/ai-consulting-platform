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
  ScatterChart,
  Scatter,
  ZAxis,
  ReferenceArea,
  ReferenceLine,
} from "recharts";
import TopHeader from "../components/TopHeader";
import CsvUploadFlow from "../components/CsvUploadFlow/CsvUploadFlow";
import { painAreaService, getApiError } from "../services/api";
import "../styles/pages/AIInterventionPainAreasTrackerRecord.css";

const PRIORITY_OPTIONS = ["High", "Medium", "Low"];
const STATUS_OPTIONS = ["Open", "In Progress", "Completed", "On Hold", "Cancelled"];
const QUADRANT_OPTIONS = ["Quick Win", "Strategic", "Fill In", "Revisit"];
const SCORE_OPTIONS = [1, 2, 3];
const PAGE_SIZE = 10;
const PRESETS_KEY = "painAreaPresets";

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

const QUADRANT_COLORS = {
  "Quick Win": "#16A34A",
  Strategic: "#2563EB",
  "Fill In": "#D97706",
  Revisit: "#94A3B8",
};

const SCORE_DIST_COLORS = ["#059669", "#D97706", "#DC2626"];

const SOLUTION_META = {
  "Generative AI Assistant": { icon: "auto_awesome", color: "#8B5CF6", badge: "bg-violet-100 text-violet-700" },
  "AI Knowledge Base": { icon: "database", color: "#0D9488", badge: "bg-teal-100 text-teal-700" },
  "Workflow Automation": { icon: "sync_alt", color: "#2563EB", badge: "bg-blue-100 text-blue-700" },
  "Predictive Analytics": { icon: "trending_up", color: "#EA580C", badge: "bg-orange-100 text-orange-700" },
  "Intelligent Search": { icon: "search", color: "#0EA5E9", badge: "bg-sky-100 text-sky-700" },
  "Document Intelligence": { icon: "description", color: "#16A34A", badge: "bg-green-100 text-green-700" },
  "AI Decision Support": { icon: "psychology", color: "#4F46E5", badge: "bg-indigo-100 text-indigo-700" },
  "Conversational AI": { icon: "forum", color: "#F43F5E", badge: "bg-rose-100 text-rose-700" },
};

const REPORT_TYPES_META = [
  {
    key: "opportunity-assessment",
    title: "AI Opportunity Assessment Report",
    icon: "insights",
    description: "Full assessment of every AI opportunity with scoring, recommendations and confidence.",
  },
  {
    key: "department-summary",
    title: "Department Summary",
    icon: "account_balance",
    description: "Where AI effort is concentrated by department, hours and recommended solutions.",
  },
  {
    key: "executive-summary",
    title: "Executive Summary",
    icon: "summarize",
    description: "One-page leadership overview with headline KPIs and top opportunities.",
  },
  {
    key: "adoption-roadmap",
    title: "AI Adoption Roadmap",
    icon: "route",
    description: "A phased 0-3-6-12 month plan to turn opportunities into live AI initiatives.",
  },
  {
    key: "opportunity-register",
    title: "Opportunity Register",
    icon: "table_view",
    description: "The complete register of every tracked opportunity with recommendations.",
  },
];

export default function AIInterventionPainAreasTrackerRecord() {
  const navigate = useNavigate();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [filterStatus, setFilterStatus] = useState("All");
  const [filterPriority, setFilterPriority] = useState("All");
  const [filterDepartment, setFilterDepartment] = useState("All");
  const [filterQuadrant, setFilterQuadrant] = useState("All");
  const [filterImpact, setFilterImpact] = useState("All");
  const [filterFeasibility, setFilterFeasibility] = useState("All");
  const [priorityScoreMin, setPriorityScoreMin] = useState("");
  const [priorityScoreMax, setPriorityScoreMax] = useState("");
  const [timeMin, setTimeMin] = useState("");
  const [timeMax, setTimeMax] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  // Sort / pagination
  const [sortKey, setSortKey] = useState("total_score");
  const [sortDir, setSortDir] = useState("desc");
  const [currentPage, setCurrentPage] = useState(1);

  // Presets
  const [presets, setPresets] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(PRESETS_KEY) || "[]");
    } catch {
      return [];
    }
  });
  const [presetName, setPresetName] = useState("");
  const [selectedPreset, setSelectedPreset] = useState("");

  // Detail panel
  const [selectedRecord, setSelectedRecord] = useState(null);

  const [isUploadFlowOpen, setUploadFlowOpen] = useState(false);
  const [lastImport, setLastImport] = useState(null);

  // Executive reports (Phase 5)
  const [reportData, setReportData] = useState(null);
  const [exportingReport, setExportingReport] = useState(null);

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

  useEffect(() => {
    if (!records.length) return;
    painAreaService
      .reports()
      .then((res) => setReportData(res.data?.data ?? res.data ?? null))
      .catch(() => setReportData(null));
  }, [records]);

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

  const getTotalScore = (record) => {
    const impact = Number(record.impact_score) || 0;
    const feasibility = Number(record.feasibility_score) || 0;
    const priority = Number(record.priority_score) || 0;
    return impact + feasibility + priority;
  };

  const filteredRecords = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    return records.filter((r) => {
      if (filterStatus !== "All" && r.status !== filterStatus) return false;
      if (filterPriority !== "All" && r.priority !== filterPriority) return false;
      if (filterDepartment !== "All" && r.department !== filterDepartment) return false;
      if (filterQuadrant !== "All" && r.quadrant !== filterQuadrant) return false;
      if (filterImpact !== "All" && Number(r.impact_score) !== Number(filterImpact)) return false;
      if (filterFeasibility !== "All" && Number(r.feasibility_score) !== Number(filterFeasibility)) return false;
      if (priorityScoreMin !== "" && (getTotalScore(r) < Number(priorityScoreMin))) return false;
      if (priorityScoreMax !== "" && (getTotalScore(r) > Number(priorityScoreMax))) return false;
      if (timeMin !== "" && (Number(r.time_spent_hrs) || 0) < Number(timeMin)) return false;
      if (timeMax !== "" && (Number(r.time_spent_hrs) || 0) > Number(timeMax)) return false;
      if (q) {
        const haystack = [
          r.process_activity,
          r.pain_area,
          r.department,
          r.ai_intervention,
          r.owner,
          r.status,
          r.quadrant,
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return true;
    });
  }, [
    records,
    filterStatus,
    filterPriority,
    filterDepartment,
    filterQuadrant,
    filterImpact,
    filterFeasibility,
    priorityScoreMin,
    priorityScoreMax,
    timeMin,
    timeMax,
    searchQuery,
  ]);

  const sortedRecords = useMemo(() => {
    const arr = [...filteredRecords];
    const dir = sortDir === "asc" ? 1 : -1;
    arr.sort((a, b) => {
      let cmp = 0;
      if (sortKey === "total_score") {
        cmp = getTotalScore(a) - getTotalScore(b);
      } else if (sortKey === "time_spent_hrs") {
        cmp = (Number(a.time_spent_hrs) || 0) - (Number(b.time_spent_hrs) || 0);
      } else if (sortKey === "impact_score" || sortKey === "feasibility_score" || sortKey === "priority_score") {
        cmp = (Number(a[sortKey]) || 0) - (Number(b[sortKey]) || 0);
      } else if (sortKey === "date" || sortKey === "target_date") {
        cmp = new Date(a[sortKey] || 0) - new Date(b[sortKey] || 0);
      } else {
        cmp = String(a[sortKey] || "").localeCompare(String(b[sortKey] || ""));
      }
      return cmp * dir;
    });
    return arr;
  }, [filteredRecords, sortKey, sortDir]);

  const totalPages = Math.max(1, Math.ceil(sortedRecords.length / PAGE_SIZE));
  const safePage = Math.min(currentPage, totalPages);
  const paginatedRecords = useMemo(() => {
    return sortedRecords.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);
  }, [sortedRecords, safePage]);

  useEffect(() => {
    setCurrentPage(1);
  }, [filterStatus, filterPriority, filterDepartment, filterQuadrant, filterImpact, filterFeasibility, priorityScoreMin, priorityScoreMax, timeMin, timeMax, searchQuery]);

  const departments = useMemo(() => {
    const set = new Set(records.map((r) => r.department).filter(Boolean));
    return Array.from(set).sort();
  }, [records]);

  const kpis = useMemo(() => {
    const total = filteredRecords.length;
    const totalHours = filteredRecords.reduce((sum, r) => sum + (Number(r.time_spent_hrs) || 0), 0);
    const scored = filteredRecords.filter((r) => r.impact_score != null);
    const avgImpact = scored.length
      ? (scored.reduce((s, r) => s + Number(r.impact_score || 0), 0) / scored.length).toFixed(1)
      : "—";
    const avgPriority = scored.length
      ? (scored.reduce((s, r) => s + Number(r.priority_score || 0), 0) / scored.length).toFixed(1)
      : "—";
    const deptSet = new Set(filteredRecords.map((r) => r.department).filter(Boolean));
    const open = filteredRecords.filter((r) => r.status === "Open").length;
    return {
      total,
      totalHours: Math.round(totalHours),
      avgImpact,
      avgPriority,
      departments: deptSet.size,
      open,
    };
  }, [filteredRecords]);

  const quadrantCounts = useMemo(() => {
    const counts = { "Quick Win": 0, Strategic: 0, "Fill In": 0, Revisit: 0 };
    filteredRecords.forEach((r) => {
      const q = r.quadrant || "Revisit";
      if (counts[q] !== undefined) counts[q] += 1;
    });
    return counts;
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

  const deptOppsData = useMemo(() => {
    const map = {};
    filteredRecords.forEach((r) => {
      const dept = r.department || "Unknown";
      if (!map[dept]) map[dept] = { department: dept, opportunities: 0 };
      map[dept].opportunities += 1;
    });
    return Object.values(map)
      .sort((a, b) => b.opportunities - a.opportunities)
      .slice(0, 8);
  }, [filteredRecords]);

  const scoreDistData = (records, field) => {
    const counts = {};
    records.forEach((r) => {
      const v = r[field];
      if (v != null) counts[v] = (counts[v] || 0) + 1;
    });
    return SCORE_OPTIONS.filter((s) => counts[s] !== undefined)
      .map((s) => ({ score: `${s}`, count: counts[s] || 0 }));
  };

  const priorityScoreDist = useMemo(() => scoreDistData(filteredRecords, "priority_score"), [filteredRecords]);
  const impactScoreDist = useMemo(() => scoreDistData(filteredRecords, "impact_score"), [filteredRecords]);
  const feasibilityScoreDist = useMemo(() => scoreDistData(filteredRecords, "feasibility_score"), [filteredRecords]);

  const leaderboard = useMemo(() => {
    return [...filteredRecords]
      .sort((a, b) => getTotalScore(b) - getTotalScore(a))
      .slice(0, 10)
      .map((r, i) => ({ rank: i + 1, record: r }));
  }, [filteredRecords]);

  const deptSummary = useMemo(() => {
    const map = {};
    filteredRecords.forEach((r) => {
      const dept = r.department || "Unknown";
      if (!map[dept]) map[dept] = { department: dept, opportunities: 0, hours: 0, scoreSum: 0, quickWins: 0 };
      map[dept].opportunities += 1;
      map[dept].hours += Number(r.time_spent_hrs) || 0;
      map[dept].scoreSum += getTotalScore(r);
      if (r.quadrant === "Quick Win") map[dept].quickWins += 1;
    });
    return Object.values(map)
      .map((d) => ({
        ...d,
        hours: Math.round(d.hours),
        avgScore: d.opportunities ? (d.scoreSum / d.opportunities).toFixed(1) : "—",
      }))
      .sort((a, b) => b.opportunities - a.opportunities);
  }, [filteredRecords]);

  const quadrantScatterData = useMemo(() => {
    const jitter = (seed) => ((seed * 37) % 21 - 10) / 50;
    return filteredRecords
      .filter((r) => r.impact_score != null && r.feasibility_score != null)
      .map((r) => ({
        name: r.process_activity || "Record",
        impact: Number(r.impact_score) + jitter(r.id ?? 1),
        feasibility: Number(r.feasibility_score) + jitter((r.id ?? 1) * 7 + 3),
        quadrant: r.quadrant || "Revisit",
        priority: r.priority,
      }));
  }, [filteredRecords]);

  const getQuadrantClass = (quadrant) => {
    const map = {
      "Quick Win": "bg-emerald-100 text-emerald-700",
      Strategic: "bg-blue-100 text-blue-700",
      "Fill In": "bg-amber-100 text-amber-700",
      Revisit: "bg-slate-100 text-slate-600",
    };
    return map[quadrant] || "bg-slate-100 text-slate-600";
  };

  const getScoreClass = (score) => {
    if (score == null) return "bg-slate-100 text-slate-600";
    if (score >= 3) return "bg-emerald-100 text-emerald-700";
    if (score === 2) return "bg-amber-100 text-amber-700";
    return "bg-slate-100 text-slate-600";
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

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  };

  const SortIcon = ({ col }) => {
    if (sortKey !== col) return <span className="pain-sort-icon pain-sort-idle">↕</span>;
    return <span className="pain-sort-icon">{sortDir === "asc" ? "▲" : "▼"}</span>;
  };

  const resetFilters = () => {
    setFilterStatus("All");
    setFilterPriority("All");
    setFilterDepartment("All");
    setFilterQuadrant("All");
    setFilterImpact("All");
    setFilterFeasibility("All");
    setPriorityScoreMin("");
    setPriorityScoreMax("");
    setTimeMin("");
    setTimeMax("");
    setSearchQuery("");
  };

  // Presets
  const savePreset = () => {
    const name = presetName.trim();
    if (!name) return;
    const preset = {
      name,
      filters: {
        status: filterStatus,
        priority: filterPriority,
        department: filterDepartment,
        quadrant: filterQuadrant,
        impact: filterImpact,
        feasibility: filterFeasibility,
        pMin: priorityScoreMin,
        pMax: priorityScoreMax,
        tMin: timeMin,
        tMax: timeMax,
        search: searchQuery,
      },
    };
    const updated = [...presets.filter((p) => p.name !== name), preset];
    setPresets(updated);
    localStorage.setItem(PRESETS_KEY, JSON.stringify(updated));
    setPresetName("");
  };

  const loadPreset = (name) => {
    const preset = presets.find((p) => p.name === name);
    if (!preset) return;
    const f = preset.filters;
    setFilterStatus(f.status || "All");
    setFilterPriority(f.priority || "All");
    setFilterDepartment(f.department || "All");
    setFilterQuadrant(f.quadrant || "All");
    setFilterImpact(f.impact || "All");
    setFilterFeasibility(f.feasibility || "All");
    setPriorityScoreMin(f.pMin ?? "");
    setPriorityScoreMax(f.pMax ?? "");
    setTimeMin(f.tMin ?? "");
    setTimeMax(f.tMax ?? "");
    setSearchQuery(f.search || "");
  };

  const deletePreset = (name) => {
    const updated = presets.filter((p) => p.name !== name);
    setPresets(updated);
    localStorage.setItem(PRESETS_KEY, JSON.stringify(updated));
    setSelectedPreset("");
  };

  const exportCsv = () => {
    const headers = [
      "Date",
      "Department",
      "Process / Activity",
      "Pain Area",
      "Current Method",
      "Frequency",
      "Hours",
      "Impact Score",
      "Feasibility Score",
      "Priority Score",
      "Total Score",
      "Quadrant",
      "Priority",
      "Status",
      "Owner",
      "Target Date",
      "AI Intervention",
      "Expected Benefit",
      "Remarks",
    ];
    const esc = (v) => {
      const s = v == null ? "" : String(v);
      return `"${s.replace(/"/g, '""')}"`;
    };
    const rows = sortedRecords.map((r) => [
      r.date,
      r.department,
      r.process_activity,
      r.pain_area,
      r.current_method,
      r.frequency,
      r.time_spent_hrs,
      r.impact_score,
      r.feasibility_score,
      r.priority_score,
      getTotalScore(r),
      r.quadrant,
      r.priority,
      r.status,
      r.owner,
      r.target_date,
      r.ai_intervention,
      r.expected_benefit,
      r.remarks,
    ]);
    const csv = [headers, ...rows].map((row) => row.map(esc).join(",")).join("\n");
    const blob = new Blob([`\uFEFF${csv}`], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `pain-area-opportunities-${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadBlob = (blob, filename) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleExportReport = async (reportType, fileFormat) => {
    const key = `${reportType}-${fileFormat}`;
    setExportingReport(key);
    try {
      const res = await painAreaService.exportReport(reportType, fileFormat);
      const contentType =
        res.data.type ||
        (fileFormat === "pdf"
          ? "application/pdf"
          : "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
      downloadBlob(
        new Blob([res.data], { type: contentType }),
        `${reportType}-${new Date().toISOString().slice(0, 10)}.${fileFormat}`
      );
    } catch (err) {
      console.error("Report export error:", err);
      alert(getApiError(err, "Failed to export report."));
    } finally {
      setExportingReport(null);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 85) return "#16A34A";
    if (confidence >= 70) return "#D97706";
    return "#64748B";
  };

  const recommendationList = useMemo(() => {
    return [...sortedRecords]
      .filter((r) => r.ai_recommendation)
      .sort((a, b) => (Number(b.ai_confidence) || 0) - (Number(a.ai_confidence) || 0))
      .slice(0, 10);
  }, [sortedRecords]);

  const solutionDistData = useMemo(() => {
    const counts = {};
    sortedRecords.forEach((r) => {
      if (r.ai_recommendation) {
        counts[r.ai_recommendation] = (counts[r.ai_recommendation] || 0) + 1;
      }
    });
    return Object.entries(counts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  }, [sortedRecords]);

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

  const QuadrantTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const entry = payload[0].payload;
      return (
        <div className="chart-tooltip">
          <p className="chart-tooltip-label">{entry.name}</p>
          <p style={{ color: QUADRANT_COLORS[entry.quadrant] }}>
            <strong>{entry.quadrant}</strong>
          </p>
          <p>
            Impact {entry.impact} · Feasibility {entry.feasibility}
          </p>
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
            <span className="pain-filter-label">Search</span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Process, department, pain area…"
              className="pain-search-input"
            />
          </div>
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
          <div className="pain-filter-group">
            <span className="pain-filter-label">Quadrant</span>
            <select
              value={filterQuadrant}
              onChange={(e) => setFilterQuadrant(e.target.value)}
              className="pain-select"
            >
              <option value="All">All</option>
              {QUADRANT_OPTIONS.map((q) => (
                <option key={q} value={q}>{q}</option>
              ))}
            </select>
          </div>
          <div className="pain-filter-group">
            <span className="pain-filter-label">Impact</span>
            <select
              value={filterImpact}
              onChange={(e) => setFilterImpact(e.target.value)}
              className="pain-select"
            >
              <option value="All">All</option>
              {SCORE_OPTIONS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <div className="pain-filter-group">
            <span className="pain-filter-label">Feasibility</span>
            <select
              value={filterFeasibility}
              onChange={(e) => setFilterFeasibility(e.target.value)}
              className="pain-select"
            >
              <option value="All">All</option>
              {SCORE_OPTIONS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <div className="pain-filter-group">
            <span className="pain-filter-label">Score</span>
            <input
              type="number"
              min={3}
              max={9}
              value={priorityScoreMin}
              onChange={(e) => setPriorityScoreMin(e.target.value)}
              placeholder="Min"
              className="pain-range-input"
            />
            <span className="pain-filter-label">–</span>
            <input
              type="number"
              min={3}
              max={9}
              value={priorityScoreMax}
              onChange={(e) => setPriorityScoreMax(e.target.value)}
              placeholder="Max"
              className="pain-range-input"
            />
          </div>
          <div className="pain-filter-group">
            <span className="pain-filter-label">Hours</span>
            <input
              type="number"
              min={0}
              value={timeMin}
              onChange={(e) => setTimeMin(e.target.value)}
              placeholder="Min"
              className="pain-range-input"
            />
            <span className="pain-filter-label">–</span>
            <input
              type="number"
              min={0}
              value={timeMax}
              onChange={(e) => setTimeMax(e.target.value)}
              placeholder="Max"
              className="pain-range-input"
            />
          </div>
          <button onClick={resetFilters} className="pain-filter-reset-btn" title="Reset filters">
            <span className="material-symbols-outlined text-[16px]">refresh</span>
            Reset
          </button>
          <div className="pain-filter-count">
            Showing <strong>{sortedRecords.length}</strong> of <strong>{records.length}</strong> records
          </div>
        </div>
      </div>

      {/* Presets */}
      <div className="pain-presets soft-shadow">
        <div className="pain-presets-inner">
          <span className="pain-filter-label">Filter presets</span>
          <select
            value={selectedPreset}
            onChange={(e) => {
              setSelectedPreset(e.target.value);
              if (e.target.value) loadPreset(e.target.value);
            }}
            className="pain-select"
          >
            <option value="">Select a preset…</option>
            {presets.map((p) => (
              <option key={p.name} value={p.name}>{p.name}</option>
            ))}
          </select>
          {selectedPreset && (
            <button onClick={() => deletePreset(selectedPreset)} className="pain-preset-delete-btn" title="Delete preset">
              Delete
            </button>
          )}
          <input
            type="text"
            value={presetName}
            onChange={(e) => setPresetName(e.target.value)}
            placeholder="New preset name…"
            className="pain-search-input"
          />
          <button onClick={savePreset} className="pain-primary-btn" disabled={!presetName.trim()}>
            Save Current Filters
          </button>
          <button onClick={exportCsv} className="pain-secondary-btn" title="Export filtered data as CSV">
            <span className="material-symbols-outlined text-[18px]">download</span>
            Export CSV
          </button>
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
          <p className="pain-kpi-sub teal">Across all opportunities</p>
        </div>
        <div className="pain-kpi-card soft-shadow border-left-green">
          <p className="pain-kpi-label">Quick Wins</p>
          <p className="pain-kpi-value green">{quadrantCounts["Quick Win"]}</p>
          <p className="pain-kpi-sub">High impact × high feasibility</p>
        </div>
        <div className="pain-kpi-card soft-shadow border-left-blue">
          <p className="pain-kpi-label">Strategic Projects</p>
          <p className="pain-kpi-value blue">{quadrantCounts["Strategic"]}</p>
          <p className="pain-kpi-sub">High impact × low feasibility</p>
        </div>
        <div className="pain-kpi-card soft-shadow border-left-amber">
          <p className="pain-kpi-label">Fill-In Opportunities</p>
          <p className="pain-kpi-value amber">{quadrantCounts["Fill In"]}</p>
          <p className="pain-kpi-sub">Low impact × high feasibility</p>
        </div>
        <div className="pain-kpi-card soft-shadow">
          <p className="pain-kpi-label">Revisit</p>
          <p className="pain-kpi-value">{quadrantCounts["Revisit"]}</p>
          <p className="pain-kpi-sub">Low impact × low feasibility</p>
        </div>
        <div className="pain-kpi-card soft-shadow">
          <p className="pain-kpi-label">Avg Impact Score</p>
          <p className="pain-kpi-value indigo">{kpis.avgImpact}</p>
          <p className="pain-kpi-sub">Of 3</p>
        </div>
        <div className="pain-kpi-card soft-shadow">
          <p className="pain-kpi-label">Avg Priority Score</p>
          <p className="pain-kpi-value indigo">{kpis.avgPriority}</p>
          <p className="pain-kpi-sub">Of 3</p>
        </div>
        <div className="pain-kpi-card soft-shadow">
          <p className="pain-kpi-label">Departments Covered</p>
          <p className="pain-kpi-value">{kpis.departments}</p>
          <p className="pain-kpi-sub">Unique departments</p>
        </div>
        <div className="pain-kpi-card soft-shadow">
          <p className="pain-kpi-label">Open Opportunities</p>
          <p className="pain-kpi-value">{kpis.open}</p>
          <p className="pain-kpi-sub">Status = Open</p>
        </div>
      </div>

      {/* Charts Row 1 - Quadrant Distribution + Hours by Dept */}
      <div className="pain-charts-grid">
        <div className="pain-panel soft-shadow">
          <h3 className="pain-h3">Quadrant Distribution</h3>
          {filteredRecords.length === 0 ? (
            <div className="pain-chart-empty">No data</div>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={QUADRANT_OPTIONS.map((q) => ({ name: q, value: quadrantCounts[q] }))} margin={{ left: 10, right: 10 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="value" name="Opportunities" radius={[6, 6, 0, 0]} barSize={40}>
                  {QUADRANT_OPTIONS.map((q) => (
                    <Cell key={q} fill={QUADRANT_COLORS[q]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
        <div className="pain-panel soft-shadow">
          <h3 className="pain-h3">Time Spent (Hrs/Month) by Department</h3>
          {departmentBarData.length === 0 ? (
            <div className="pain-chart-empty">No data</div>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
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
      </div>

      {/* Charts Row 2 - Dept Opps + Status */}
      <div className="pain-charts-grid">
        <div className="pain-panel soft-shadow">
          <h3 className="pain-h3">Department vs Opportunities</h3>
          {deptOppsData.length === 0 ? (
            <div className="pain-chart-empty">No data</div>
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={deptOppsData} margin={{ left: 10, right: 10 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="department" tick={{ fontSize: 11 }} interval={0} angle={-20} textAnchor="end" height={60} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="opportunities" name="Opportunities" fill="#4F46E5" radius={[6, 6, 0, 0]} barSize={30} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
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
      </div>

      {/* Charts Row 3 - Score Distributions */}
      <div className="pain-charts-grid">
        <div className="pain-panel soft-shadow">
          <h3 className="pain-h3">Priority Score Distribution</h3>
          {priorityScoreDist.length === 0 ? (
            <div className="pain-chart-empty">No data</div>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={priorityScoreDist} margin={{ left: 10, right: 10 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="score" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" name="Records" radius={[6, 6, 0, 0]} barSize={44}>
                  {priorityScoreDist.map((entry, i) => (
                    <Cell key={i} fill={SCORE_DIST_COLORS[Number(entry.score) - 1] || "#0D9488"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
        <div className="pain-panel soft-shadow">
          <h3 className="pain-h3">Impact Score Distribution</h3>
          {impactScoreDist.length === 0 ? (
            <div className="pain-chart-empty">No data</div>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={impactScoreDist} margin={{ left: 10, right: 10 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="score" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" name="Records" radius={[6, 6, 0, 0]} barSize={44}>
                  {impactScoreDist.map((entry, i) => (
                    <Cell key={i} fill={SCORE_DIST_COLORS[Number(entry.score) - 1] || "#0D9488"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
        <div className="pain-panel soft-shadow">
          <h3 className="pain-h3">Feasibility Score Distribution</h3>
          {feasibilityScoreDist.length === 0 ? (
            <div className="pain-chart-empty">No data</div>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={feasibilityScoreDist} margin={{ left: 10, right: 10 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="score" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" name="Records" radius={[6, 6, 0, 0]} barSize={44}>
                  {feasibilityScoreDist.map((entry, i) => (
                    <Cell key={i} fill={SCORE_DIST_COLORS[Number(entry.score) - 1] || "#0D9488"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
        <div className="pain-panel soft-shadow">
          <h3 className="pain-h3">Priority Breakdown</h3>
          {priorityPieData.length === 0 ? (
            <div className="pain-chart-empty">No data</div>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={priorityPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
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

      {/* Quadrant Matrix */}
      <div className="pain-panel soft-shadow">
        <div className="pain-table-header">
          <h3 className="pain-h3">Impact × Feasibility Quadrant Matrix</h3>
          <div className="pain-quadrant-legend">
            {QUADRANT_OPTIONS.map((q) => (
              <span key={q} className="pain-quadrant-legend-item">
                <span className="pain-quadrant-legend-dot" style={{ background: QUADRANT_COLORS[q] }} />
                {q} ({quadrantCounts[q]})
              </span>
            ))}
          </div>
        </div>
        {quadrantScatterData.length === 0 ? (
          <div className="pain-chart-empty">No data</div>
        ) : (
          <ResponsiveContainer width="100%" height={340}>
            <ScatterChart margin={{ top: 10, right: 30, bottom: 30, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis
                type="number"
                dataKey="impact"
                name="Impact"
                domain={[0.5, 3.5]}
                ticks={[1, 2, 3]}
                tick={{ fontSize: 12 }}
                label={{ value: "Impact Score", position: "insideBottom", offset: -18, fontSize: 12 }}
              />
              <YAxis
                type="number"
                dataKey="feasibility"
                name="Feasibility"
                domain={[0.5, 3.5]}
                ticks={[1, 2, 3]}
                tick={{ fontSize: 12 }}
                label={{ value: "Feasibility Score", angle: -90, position: "insideLeft", fontSize: 12 }}
              />
              <ZAxis range={[120, 120]} />
              <ReferenceLine x={2} stroke="#CBD5E1" strokeDasharray="4 4" />
              <ReferenceLine y={2} stroke="#CBD5E1" strokeDasharray="4 4" />
              <ReferenceArea x1={2} x2={3.5} y1={2} y2={3.5} fill="#16A34A" fillOpacity={0.08} />
              <ReferenceArea x1={2} x2={3.5} y1={0.5} y2={2} fill="#2563EB" fillOpacity={0.08} />
              <ReferenceArea x1={0.5} x2={2} y1={2} y2={3.5} fill="#D97706" fillOpacity={0.08} />
              <ReferenceArea x1={0.5} x2={2} y1={0.5} y2={2} fill="#94A3B8" fillOpacity={0.08} />
              <Tooltip content={<QuadrantTooltip />} />
              <Scatter data={quadrantScatterData} isAnimationActive={false}>
                {quadrantScatterData.map((entry, index) => (
                  <Cell
                    key={`scatter-${index}`}
                    fill={QUADRANT_COLORS[entry.quadrant]}
                    stroke="#FFFFFF"
                    strokeWidth={1}
                  />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Top Opportunities Leaderboard */}
      <div className="pain-panel soft-shadow">
        <div className="pain-table-header">
          <h3 className="pain-h3">Top AI Opportunities</h3>
          <span className="pain-subtitle-sm">Ranked by total score (impact + feasibility + priority)</span>
        </div>
        {leaderboard.length === 0 ? (
          <div className="pain-chart-empty">No data</div>
        ) : (
          <div className="pain-table-wrap">
            <table className="pain-table">
              <thead>
                <tr className="pain-table-head-row">
                  <th className="pain-th text-center">Rank</th>
                  <th className="pain-th">Department</th>
                  <th className="pain-th">Process / Activity</th>
                  <th className="pain-th text-center">Score</th>
                  <th className="pain-th">Quadrant</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.map(({ rank, record }) => (
                  <tr key={record.id} className="pain-row pain-row-clickable" onClick={() => setSelectedRecord(record)}>
                    <td className="pain-td text-center">
                      <span className={`pain-rank-badge ${rank <= 3 ? "pain-rank-top" : ""}`}>{rank}</span>
                    </td>
                    <td className="pain-td">{record.department || "—"}</td>
                    <td className="pain-td max-220">
                      <p className="truncate" title={record.process_activity}>
                        {record.process_activity || "—"}
                      </p>
                    </td>
                    <td className="pain-td text-center">
                      <span className="pain-total-score">{getTotalScore(record)}</span>
                    </td>
                    <td className="pain-td">
                      <span className={`pain-pill ${getQuadrantClass(record.quadrant)}`}>
                        {record.quadrant || "—"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* AI Recommendations (Modules 4.1 - 4.3) */}
      <div className="pain-panel soft-shadow pain-rec-panel">
        <div className="pain-table-header">
          <div>
            <h3 className="pain-h3">AI Recommendations & Confidence</h3>
            <span className="pain-subtitle-sm">
              Module 4 · The platform suggests the best AI solution for each opportunity, with confidence and reasoning
            </span>
          </div>
          <span className="pain-rec-note">
            <span className="material-symbols-outlined text-[16px]">auto_awesome</span>
            Engine: pain area · current method · AI intervention · impact area · time · priority · feasibility
          </span>
        </div>

        {recommendationList.length === 0 ? (
          <div className="pain-chart-empty">No recommendations yet — add records to see AI suggestions.</div>
        ) : (
          <div className="pain-rec-grid">
            {/* Left: solution distribution */}
            <div className="pain-rec-dist">
              <h4 className="pain-rec-h4">Recommended solutions</h4>
              {solutionDistData.map(({ name, value }) => {
                const meta = SOLUTION_META[name] || {};
                const pct = sortedRecords.length
                  ? Math.round((value / sortedRecords.length) * 100)
                  : 0;
                return (
                  <div key={name} className="pain-rec-dist-row">
                    <span className="pain-rec-dist-label" title={name}>
                      <span
                        className="material-symbols-outlined pain-rec-dist-icon"
                        style={{ color: meta.color }}
                      >
                        {meta.icon || "smart_toy"}
                      </span>
                      {name}
                    </span>
                    <div className="pain-conf-bar">
                      <div
                        className="pain-conf-fill"
                        style={{ width: `${pct}%`, background: meta.color }}
                      />
                    </div>
                    <span className="pain-rec-dist-count">{value}</span>
                  </div>
                );
              })}
            </div>

            {/* Right: per-record recommendations */}
            <div className="pain-rec-list">
              <h4 className="pain-rec-h4">Top recommendations</h4>
              {recommendationList.map((record) => {
                const meta = SOLUTION_META[record.ai_recommendation] || {};
                const conf = Number(record.ai_confidence) || 0;
                return (
                  <div
                    key={record.id}
                    className="pain-rec-card"
                    onClick={() => setSelectedRecord(record)}
                  >
                    <div className="pain-rec-card-head">
                      <div className="pain-rec-card-title">
                        <span className="pain-rec-solution" style={{ borderColor: meta.color }}>
                          <span
                            className="material-symbols-outlined pain-rec-solution-icon"
                            style={{ color: meta.color }}
                          >
                            {meta.icon || "smart_toy"}
                          </span>
                          {record.ai_recommendation}
                        </span>
                        <span className="pain-rec-process" title={record.process_activity}>
                          {record.process_activity || "Untitled opportunity"}
                          <span className="pain-rec-dept">
                            {record.department ? ` · ${record.department}` : ""}
                          </span>
                        </span>
                      </div>
                      <div className="pain-rec-conf">
                        <span className="pain-rec-conf-pct" style={{ color: getConfidenceColor(conf) }}>
                          {conf}%
                        </span>
                        <div className="pain-conf-bar pain-conf-bar-sm">
                          <div
                            className="pain-conf-fill"
                            style={{ width: `${conf}%`, background: getConfidenceColor(conf) }}
                          />
                        </div>
                      </div>
                    </div>
                    <p className="pain-rec-reason">{record.ai_reasoning}</p>
                    <div className="pain-rec-card-foot">
                      <span className={`pain-pill ${getQuadrantClass(record.quadrant)}`}>
                        {record.quadrant || "—"}
                      </span>
                      <span className="pain-total-score">Score {getTotalScore(record)}</span>
                      <span className="pain-subtitle-sm">Click to view details</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Department Summary */}
      <div className="pain-panel soft-shadow">
        <div className="pain-table-header">
          <h3 className="pain-h3">Department Summary</h3>
          <span className="pain-subtitle-sm">Where should we focus next?</span>
        </div>
        {deptSummary.length === 0 ? (
          <div className="pain-chart-empty">No data</div>
        ) : (
          <div className="pain-table-wrap">
            <table className="pain-table">
              <thead>
                <tr className="pain-table-head-row">
                  <th className="pain-th">Department</th>
                  <th className="pain-th text-center">Opportunities</th>
                  <th className="pain-th text-center">Hours / Month</th>
                  <th className="pain-th text-center">Avg Score</th>
                  <th className="pain-th text-center">Quick Wins</th>
                </tr>
              </thead>
              <tbody>
                {deptSummary.map((d) => (
                  <tr key={d.department} className="pain-row">
                    <td className="pain-td">{d.department}</td>
                    <td className="pain-td text-center">{d.opportunities}</td>
                    <td className="pain-td text-center">{d.hours}</td>
                    <td className="pain-td text-center">
                      <span className="pain-total-score">{d.avgScore}</span>
                    </td>
                    <td className="pain-td text-center">
                      <span className={`pain-pill ${d.quickWins > 0 ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>
                        {d.quickWins}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Executive Reports (Phase 5) */}
      <div className="pain-panel soft-shadow">
        <div className="pain-table-header">
          <div>
            <h3 className="pain-h3">Executive Reports</h3>
            <span className="pain-subtitle-sm">
              Phase 5 · Generate & export executive reports as PDF or Excel
            </span>
          </div>
          {reportData && (
            <span className="pain-filter-count">
              {reportData.report_count} opportunities · {reportData.total_hours} hrs/month ·{" "}
              {reportData.departments} departments
            </span>
          )}
        </div>

        <div className="pain-report-grid">
          {REPORT_TYPES_META.map((report) => (
            <div key={report.key} className="pain-report-card soft-shadow">
              <div className="pain-report-icon">
                <span className="material-symbols-outlined">{report.icon}</span>
              </div>
              <h4 className="pain-report-title">{report.title}</h4>
              <p className="pain-report-desc">{report.description}</p>
              <div className="pain-report-actions">
                <button
                  className="pain-report-btn pdf"
                  disabled={!records.length || exportingReport === `${report.key}-pdf`}
                  onClick={() => handleExportReport(report.key, "pdf")}
                >
                  <span className="material-symbols-outlined text-[16px]">picture_as_pdf</span>
                  {exportingReport === `${report.key}-pdf` ? "Generating…" : "PDF"}
                </button>
                <button
                  className="pain-report-btn xlsx"
                  disabled={!records.length || exportingReport === `${report.key}-xlsx`}
                  onClick={() => handleExportReport(report.key, "xlsx")}
                >
                  <span className="material-symbols-outlined text-[16px]">grid_on</span>
                  {exportingReport === `${report.key}-xlsx` ? "Generating…" : "Excel"}
                </button>
              </div>
            </div>
          ))}
        </div>
        {!records.length && (
          <div className="pain-subtitle-sm" style={{ marginTop: 12 }}>
            Add records to unlock report exports.
          </div>
        )}
      </div>

      {/* Records Table */}
      <div className="pain-panel soft-shadow">
        <div className="pain-table-header">
          <h3 className="pain-h3">Records</h3>
          <span className="pain-subtitle-sm">Click a row to view details</span>
        </div>
        {loading ? (
          <div className="pain-loading">
            <div className="pain-spinner" />
          </div>
        ) : sortedRecords.length === 0 ? (
          <div className="pain-empty">
            <span className="material-symbols-outlined pain-empty-icon">table_chart</span>
            <p>No records found. Click “Add New Record” to get started.</p>
          </div>
        ) : (
          <>
            <div className="pain-table-wrap">
              <table className="pain-table">
                <thead>
                  <tr className="pain-table-head-row">
                    <th className="pain-th pain-sortable" onClick={() => handleSort("date")}>
                      Date <SortIcon col="date" />
                    </th>
                    <th className="pain-th pain-sortable" onClick={() => handleSort("department")}>
                      Department <SortIcon col="department" />
                    </th>
                    <th className="pain-th pain-sortable" onClick={() => handleSort("process_activity")}>
                      Process / Activity <SortIcon col="process_activity" />
                    </th>
                    <th className="pain-th pain-sortable" onClick={() => handleSort("time_spent_hrs")}>
                      Hours <SortIcon col="time_spent_hrs" />
                    </th>
                    <th className="pain-th pain-sortable text-center" onClick={() => handleSort("impact_score")}>
                      Impact <SortIcon col="impact_score" />
                    </th>
                    <th className="pain-th pain-sortable text-center" onClick={() => handleSort("feasibility_score")}>
                      Feasibility <SortIcon col="feasibility_score" />
                    </th>
                    <th className="pain-th pain-sortable text-center" onClick={() => handleSort("total_score")}>
                      Score <SortIcon col="total_score" />
                    </th>
                    <th className="pain-th pain-sortable" onClick={() => handleSort("quadrant")}>
                      Quadrant <SortIcon col="quadrant" />
                    </th>
                    <th className="pain-th pain-sortable" onClick={() => handleSort("status")}>
                      Status <SortIcon col="status" />
                    </th>
                    <th className="pain-th text-center">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedRecords.map((record) => (
                    <tr
                      key={record.id}
                      className="pain-row pain-row-clickable"
                      onClick={() => setSelectedRecord(record)}
                    >
                      <td className="pain-td nowrap">
                        {record.date ? new Date(record.date).toLocaleDateString() : "—"}
                      </td>
                      <td className="pain-td">{record.department || "—"}</td>
                      <td className="pain-td max-220">
                        <p className="truncate" title={record.process_activity}>
                          {record.process_activity || "—"}
                        </p>
                      </td>
                      <td className="pain-td nowrap">
                        {record.time_spent_hrs != null ? `${record.time_spent_hrs} hrs` : "—"}
                      </td>
                      <td className="pain-td text-center">
                        <span className={`pain-score-badge ${getScoreClass(record.impact_score)}`}>
                          {record.impact_score ?? "—"}
                        </span>
                      </td>
                      <td className="pain-td text-center">
                        <span className={`pain-score-badge ${getScoreClass(record.feasibility_score)}`}>
                          {record.feasibility_score ?? "—"}
                        </span>
                      </td>
                      <td className="pain-td text-center">
                        <span className="pain-total-score">
                          {getTotalScore(record)}
                        </span>
                      </td>
                      <td className="pain-td">
                        <span className={`pain-pill ${getQuadrantClass(record.quadrant)}`}>
                          {record.quadrant || "—"}
                        </span>
                      </td>
                      <td className="pain-td">
                        <span className={`pain-pill ${getStatusClass(record.status)}`}>
                          {record.status || "—"}
                        </span>
                      </td>
                      <td className="pain-td">
                        <div className="pain-actions" onClick={(e) => e.stopPropagation()}>
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

            {/* Pagination */}
            <div className="pain-pagination">
              <span className="pain-filter-label">
                Page {safePage} of {totalPages} · {sortedRecords.length} records
              </span>
              <div className="pain-pagination-btns">
                <button
                  className="pain-page-btn"
                  disabled={safePage <= 1}
                  onClick={() => setCurrentPage(safePage - 1)}
                >
                  ← Prev
                </button>
                {Array.from({ length: totalPages }, (_, i) => i + 1)
                  .filter((p) => p === 1 || p === totalPages || Math.abs(p - safePage) <= 1)
                  .reduce((acc, p, i, arr) => {
                    if (i > 0 && p - arr[i - 1] > 1) acc.push("…");
                    acc.push(p);
                    return acc;
                  }, [])
                  .map((p, i) =>
                    p === "…" ? (
                      <span key={`gap-${i}`} className="pain-page-gap">…</span>
                    ) : (
                      <button
                        key={p}
                        className={`pain-page-btn ${p === safePage ? "active" : ""}`}
                        onClick={() => setCurrentPage(p)}
                      >
                        {p}
                      </button>
                    )
                  )}
                <button
                  className="pain-page-btn"
                  disabled={safePage >= totalPages}
                  onClick={() => setCurrentPage(safePage + 1)}
                >
                  Next →
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Opportunity Detail Panel */}
      {selectedRecord && (
        <div className="pain-detail-overlay" onClick={() => setSelectedRecord(null)}>
          <div className="pain-detail-panel" onClick={(e) => e.stopPropagation()}>
            <div className="pain-detail-header">
              <div>
                <h3 className="pain-h3">{selectedRecord.process_activity || "Opportunity"}</h3>
                <p className="pain-detail-sub">
                  {selectedRecord.department || "No department"} ·{" "}
                  {selectedRecord.date ? new Date(selectedRecord.date).toLocaleDateString() : "No date"}
                </p>
              </div>
              <button className="pain-detail-close" onClick={() => setSelectedRecord(null)} aria-label="Close">
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>

            <div className="pain-rec-detail">
              <div className="pain-rec-detail-head">
                <span
                  className="pain-rec-solution"
                  style={{
                    borderColor: (SOLUTION_META[selectedRecord.ai_recommendation] || {}).color,
                  }}
                >
                  <span
                    className="material-symbols-outlined pain-rec-solution-icon"
                    style={{
                      color: (SOLUTION_META[selectedRecord.ai_recommendation] || {}).color,
                    }}
                  >
                    {(SOLUTION_META[selectedRecord.ai_recommendation] || {}).icon || "smart_toy"}
                  </span>
                  AI Recommendation: {selectedRecord.ai_recommendation || "—"}
                </span>
                <div className="pain-rec-detail-conf">
                  <span
                    className="pain-rec-conf-pct"
                    style={{ color: getConfidenceColor(Number(selectedRecord.ai_confidence) || 0) }}
                  >
                    {selectedRecord.ai_confidence != null ? `${selectedRecord.ai_confidence}% confidence` : "—"}
                  </span>
                  <div className="pain-conf-bar">
                    <div
                      className="pain-conf-fill"
                      style={{
                        width: `${selectedRecord.ai_confidence ?? 0}%`,
                        background: getConfidenceColor(Number(selectedRecord.ai_confidence) || 0),
                      }}
                    />
                  </div>
                </div>
              </div>
              {selectedRecord.ai_reasoning && (
                <p className="pain-rec-detail-reason">{selectedRecord.ai_reasoning}</p>
              )}
            </div>

            <div className="pain-detail-scores">
              <div className="pain-detail-score-card">
                <span className="pain-detail-score-label">Impact</span>
                <span className={`pain-score-badge pain-score-badge-lg ${getScoreClass(selectedRecord.impact_score)}`}>
                  {selectedRecord.impact_score ?? "—"}
                </span>
              </div>
              <div className="pain-detail-score-card">
                <span className="pain-detail-score-label">Feasibility</span>
                <span className={`pain-score-badge pain-score-badge-lg ${getScoreClass(selectedRecord.feasibility_score)}`}>
                  {selectedRecord.feasibility_score ?? "—"}
                </span>
              </div>
              <div className="pain-detail-score-card">
                <span className="pain-detail-score-label">Priority</span>
                <span className={`pain-score-badge pain-score-badge-lg ${getScoreClass(selectedRecord.priority_score)}`}>
                  {selectedRecord.priority_score ?? "—"}
                </span>
              </div>
              <div className="pain-detail-score-card">
                <span className="pain-detail-score-label">Total</span>
                <span className="pain-total-score pain-total-score-lg">{getTotalScore(selectedRecord)}</span>
              </div>
              <div className="pain-detail-score-card">
                <span className="pain-detail-score-label">Quadrant</span>
                <span className={`pain-pill ${getQuadrantClass(selectedRecord.quadrant)}`}>
                  {selectedRecord.quadrant || "—"}
                </span>
              </div>
            </div>

            <div className="pain-detail-grid">
              <div className="pain-detail-field">
                <span className="pain-detail-field-label">Pain Area</span>
                <p>{selectedRecord.pain_area || "—"}</p>
              </div>
              <div className="pain-detail-field">
                <span className="pain-detail-field-label">Current Method</span>
                <p>{selectedRecord.current_method || "—"}</p>
              </div>
              <div className="pain-detail-field">
                <span className="pain-detail-field-label">Frequency</span>
                <p>{selectedRecord.frequency || "—"}</p>
              </div>
              <div className="pain-detail-field">
                <span className="pain-detail-field-label">Time Spent / Month</span>
                <p>{selectedRecord.time_spent_hrs != null ? `${selectedRecord.time_spent_hrs} hrs` : "—"}</p>
              </div>
              <div className="pain-detail-field">
                <span className="pain-detail-field-label">AI Intervention Required</span>
                <p>{selectedRecord.ai_intervention || "—"}</p>
              </div>
              <div className="pain-detail-field">
                <span className="pain-detail-field-label">Expected Benefit</span>
                <p>{selectedRecord.expected_benefit || "—"}</p>
              </div>
              <div className="pain-detail-field">
                <span className="pain-detail-field-label">Owner</span>
                <p>{selectedRecord.owner || "—"}</p>
              </div>
              <div className="pain-detail-field">
                <span className="pain-detail-field-label">Status</span>
                <p>
                  <span className={`pain-pill ${getStatusClass(selectedRecord.status)}`}>
                    {selectedRecord.status || "—"}
                  </span>
                </p>
              </div>
              <div className="pain-detail-field">
                <span className="pain-detail-field-label">Priority</span>
                <p>{selectedRecord.priority || "—"}</p>
              </div>
              <div className="pain-detail-field">
                <span className="pain-detail-field-label">Target Date</span>
                <p>
                  {selectedRecord.target_date
                    ? new Date(selectedRecord.target_date).toLocaleDateString()
                    : "—"}
                </p>
              </div>
              <div className="pain-detail-field pain-detail-field-full">
                <span className="pain-detail-field-label">Remarks</span>
                <p>{selectedRecord.remarks || "—"}</p>
              </div>
            </div>

            <div className="pain-detail-footer">
              <button
                className="pain-secondary-btn"
                onClick={() => navigate(`/ai-pain-areas/${selectedRecord.id}/edit`, { state: { record: selectedRecord } })}
              >
                <span className="material-symbols-outlined text-[18px]">edit</span>
                Edit Record
              </button>
              <button className="pain-primary-btn" onClick={() => setSelectedRecord(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

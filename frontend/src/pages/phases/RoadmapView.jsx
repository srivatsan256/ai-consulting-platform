import React, { useState, useMemo } from "react";

const PHASES = [
  { id: 1, name: "Quick Wins", short: "Phase 1", color: "#16A34A", desc: "Quadrant = Quick Win AND Total Score >= 7" },
  { id: 2, name: "Major Projects", short: "Phase 2", color: "#F59E0B", desc: "Quadrant = Major Project" },
  { id: 3, name: "Strategic Initiatives", short: "Phase 3", color: "#2563EB", desc: "Total Score between 4 and 6" },
  { id: 4, name: "Future Consideration", short: "Phase 4", color: "#94A3B8", desc: "Quadrant = Reconsider (maps to Revisit)" },
];

const STATUS_OPTIONS = ["Open", "In Progress", "Completed", "On Hold", "Cancelled"];
const PRIORITY_OPTIONS = ["High", "Medium", "Low"];
const QUADRANT_OPTIONS = ["Quick Win", "Strategic", "Fill In", "Revisit", "Major Project", "Reconsider"];

function classifyPhase(q, totalScore) {
  if (q === "Quick Win" && totalScore >= 7) return 1;
  if (q === "Major Project") return 2;
  if (totalScore >= 4 && totalScore <= 6) return 3;
  if (q === "Revisit" || q === "Reconsider") return 4;
  return null;
}

export default function RoadmapView({ records }) {
  const [statusFilter, setStatusFilter] = useState("");
  const [deptFilter, setDeptFilter] = useState("");
  const [ownerFilter, setOwnerFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [quadrantFilter, setQuadrantFilter] = useState("");

  const departments = useMemo(() => {
    const s = new Set(records.map((r) => r.department).filter(Boolean));
    return Array.from(s).sort();
  }, [records]);

  const owners = useMemo(() => {
    const s = new Set(records.map((r) => r.owner).filter(Boolean));
    return Array.from(s).sort();
  }, [records]);

  const inScope = (r) => {
    if (statusFilter && r.status !== statusFilter) return false;
    if (deptFilter && r.department !== deptFilter) return false;
    if (ownerFilter && r.owner !== ownerFilter) return false;
    if (priorityFilter && r.priority !== priorityFilter) return false;
    if (quadrantFilter && r.quadrant !== quadrantFilter) return false;
    return true;
  };

  const { phases, summary } = useMemo(() => {
    const buckets = { 1: [], 2: [], 3: [], 4: [] };
    const counts = { 1: 0, 2: 0, 3: 0, 4: 0 };
    let totalHours = 0;
    records.forEach((r) => {
      if (!inScope(r)) return;
      const q = r.quadrant || "";
      const totalScore = Number(r.total_score) || 0;
      totalHours += Number(r.time_spent_hrs) || 0;
      const phase = classifyPhase(q, totalScore);
      if (phase) {
        buckets[phase].push(r);
        counts[phase] += 1;
      }
    });
    return {
      phases: buckets,
      summary: {
        total: records.filter(inScope).length,
        counts,
        totalHours: Math.round(totalHours * 100) / 100,
      },
    };
  }, [records, statusFilter, deptFilter, ownerFilter, priorityFilter, quadrantFilter]);

  return (
    <div className="roadmap-view">
      <div className="pain-panel soft-shadow">
        <div className="pain-table-header">
          <div>
            <h3 className="pain-h3">AI Roadmap Builder</h3>
            <span className="pain-subtitle-sm">Phase 6 · Auto-classified opportunities across implementation phases</span>
          </div>
        </div>
        <div className="pain-filters-inner" style={{ margin: "12px 0", flexWrap: "wrap" }}>
          <div className="pain-filter-group">
            <span className="pain-filter-label">Status</span>
            <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="pain-select">
              <option value="">All</option>
              {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="pain-filter-group">
            <span className="pain-filter-label">Department</span>
            <select value={deptFilter} onChange={(e) => setDeptFilter(e.target.value)} className="pain-select">
              <option value="">All</option>
              {departments.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
          <div className="pain-filter-group">
            <span className="pain-filter-label">Owner</span>
            <select value={ownerFilter} onChange={(e) => setOwnerFilter(e.target.value)} className="pain-select">
              <option value="">All</option>
              {owners.map((o) => <option key={o} value={o}>{o}</option>)}
            </select>
          </div>
          <div className="pain-filter-group">
            <span className="pain-filter-label">Priority</span>
            <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)} className="pain-select">
              <option value="">All</option>
              {PRIORITY_OPTIONS.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div className="pain-filter-group">
            <span className="pain-filter-label">Quadrant</span>
            <select value={quadrantFilter} onChange={(e) => setQuadrantFilter(e.target.value)} className="pain-select">
              <option value="">All</option>
              {QUADRANT_OPTIONS.map((q) => <option key={q} value={q}>{q}</option>)}
            </select>
          </div>
        </div>
      </div>

      <div className="pain-kpi-grid">
        <div className="pain-kpi-card soft-shadow">
          <p className="pain-kpi-label">Total Projects</p>
          <p className="pain-kpi-value">{summary.total}</p>
          <p className="pain-kpi-sub">In scope</p>
        </div>
        {PHASES.map((p) => (
          <div key={p.id} className="pain-kpi-card soft-shadow" style={{ borderLeft: `3px solid ${p.color}` }}>
            <p className="pain-kpi-label">{p.name}</p>
            <p className="pain-kpi-value">{summary.counts[p.id]}</p>
            <p className="pain-kpi-sub">{p.short}</p>
          </div>
        ))}
        <div className="pain-kpi-card soft-shadow">
          <p className="pain-kpi-label">Est. Hours Saved</p>
          <p className="pain-kpi-value">{summary.totalHours}</p>
          <p className="pain-kpi-sub">Across portfolio</p>
        </div>
      </div>

      <div className="roadmap-timeline">
        {PHASES.map((phase) => {
          const list = phases[phase.id];
          return (
            <div key={phase.id} className="pain-panel soft-shadow" style={{ borderTop: `3px solid ${phase.color}` }}>
              <div className="pain-table-header">
                <div>
                  <h3 className="pain-h3">{phase.name}</h3>
                  <span className="pain-subtitle-sm">{phase.desc}</span>
                </div>
                <span className="pain-filter-count">{list.length} projects</span>
              </div>
              {list.length === 0 ? (
                <div className="pain-empty">
                  <span className="material-symbols-outlined pain-empty-icon">deployed_code</span>
                  <p>No opportunities in this phase.</p>
                </div>
              ) : (
                <div style={{ overflowX: "auto" }}>
                  <table className="pain-table">
                    <thead>
                      <tr><th>Process</th><th>Department</th><th>Owner</th><th>Est. Hours</th><th>Status</th><th>Score</th><th>Quadrant</th></tr>
                    </thead>
                    <tbody>
                      {list.map((r) => (
                        <tr key={r.id}>
                          <td>{r.process_activity || "—"}</td>
                          <td>{r.department || "—"}</td>
                          <td>{r.owner || "—"}</td>
                          <td>{Number(r.time_spent_hrs) || 0}</td>
                          <td><span className="pain-pill bg-slate-100 text-slate-700">{r.status || "—"}</span></td>
                          <td>{Number(r.total_score) || 0}</td>
                          <td><span className="pain-pill bg-indigo-100 text-indigo-700">{r.quadrant || "—"}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

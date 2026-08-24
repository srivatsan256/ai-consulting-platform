import React from "react";

/* ──────────────────────────────────────────────────────────────
   Scoring Config Panel
   A read-only reference drawer that documents the scoring rules
   used by the AI Intervention Pain Areas Tracker.
   ────────────────────────────────────────────────────────────── */

const QUADRANT_STYLE = {
  "Quick Win":     { bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-700", dot: "bg-emerald-500" },
  "Major Project": { bg: "bg-blue-50",    border: "border-blue-200",    text: "text-blue-700",    dot: "bg-blue-500" },
  "Fill In":       { bg: "bg-amber-50",   border: "border-amber-200",   text: "text-amber-700",   dot: "bg-amber-500" },
  "Reconsider":    { bg: "bg-red-50",     border: "border-red-200",     text: "text-red-700",     dot: "bg-red-500" },
  "Needs Input":   { bg: "bg-slate-50",   border: "border-slate-200",   text: "text-slate-500",   dot: "bg-slate-400" },
};

function QuadrantChip({ label }) {
  const s = QUADRANT_STYLE[label] || QUADRANT_STYLE["Needs Input"];
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${s.bg} ${s.border} ${s.text}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
      {label}
    </span>
  );
}

function SectionTitle({ icon, children }) {
  return (
    <div className="flex items-center gap-2 mb-3">
      <span className="material-symbols-outlined text-primary text-[20px]">{icon}</span>
      <h3 className="text-sm font-bold text-on-surface">{children}</h3>
    </div>
  );
}

function ScoreTable({ rows, headers }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-outline-variant/20">
      <table className="w-full text-xs">
        <thead className="bg-surface-container-low">
          <tr>
            {headers.map((h) => (
              <th key={h} className="px-3 py-2 text-left text-on-surface-variant font-semibold">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-outline-variant/10">
          {rows.map((row, i) => (
            <tr key={i} className="hover:bg-surface-container-lowest transition-colors">
              {row.map((cell, j) => (
                <td key={j} className="px-3 py-2 text-on-surface">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function ScoringConfigPanel({ onClose }) {
  return (
    /* Overlay */
    <div
      className="fixed inset-0 z-50 flex justify-end"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/30 backdrop-blur-[2px]" onClick={onClose} />

      {/* Drawer */}
      <div className="relative z-10 w-full max-w-xl bg-white h-full shadow-2xl flex flex-col overflow-hidden animate-slide-in-right">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-outline-variant/20 bg-gradient-to-r from-primary/5 to-transparent flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-primary/10 flex items-center justify-center">
              <span className="material-symbols-outlined text-primary text-[20px]">tune</span>
            </div>
            <div>
              <h2 className="text-base font-bold text-on-surface">Scoring Config</h2>
              <p className="text-xs text-on-surface-variant">Reference — all scoring is formula-driven</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-surface-container transition-colors text-on-surface-variant"
            title="Close"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Scrollable body */}
        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-6">

          {/* Impact Score */}
          <section>
            <SectionTitle icon="bolt">Impact Score (1–5)</SectionTitle>
            <p className="text-xs text-on-surface-variant mb-3">
              Derived from <strong>Time Spent / Month (hrs)</strong>. Higher hours = higher pain = higher impact.
            </p>
            <ScoreTable
              headers={["Time Spent / Month", "Impact Score", "Label"]}
              rows={[
                ["< 1 hr",      "1", "Negligible"],
                ["1 – 5 hrs",   "2", "Minor"],
                ["5 – 10 hrs",  "3", "Moderate"],
                ["10 – 40 hrs", "4", "Significant"],
                ["≥ 40 hrs",    "5", "Critical"],
                ["Missing",     "—", "Needs Input (no score)"],
              ]}
            />
            <p className="mt-2 text-xs text-on-surface-variant italic">
              Default for missing data: <strong>"Needs Input"</strong> — the row will not appear in any quadrant until this field is filled.
            </p>
          </section>

          <hr className="border-outline-variant/20" />

          {/* Feasibility Score */}
          <section>
            <SectionTitle icon="check_circle">Feasibility Score (1–5)</SectionTitle>
            <p className="text-xs text-on-surface-variant mb-3">
              Derived from the <strong>Feasibility</strong> field (High / Medium / Low).
            </p>
            <ScoreTable
              headers={["Feasibility", "Score"]}
              rows={[
                ["High",   "5"],
                ["Medium", "3"],
                ["Low",    "1"],
              ]}
            />
          </section>

          <hr className="border-outline-variant/20" />

          {/* Priority Score */}
          <section>
            <SectionTitle icon="priority_high">Overall Priority Score (1–25)</SectionTitle>
            <div className="rounded-xl border border-outline-variant/20 bg-surface-container-lowest p-4">
              <p className="text-sm font-mono text-center text-on-surface font-bold">
                Priority Score = Impact Score × Feasibility Score
              </p>
              <p className="text-xs text-center text-on-surface-variant mt-1">Range: 1 – 25 &nbsp;·&nbsp; Higher = more urgent AND more doable</p>
            </div>
          </section>

          <hr className="border-outline-variant/20" />

          {/* Quadrant Assignment */}
          <section>
            <SectionTitle icon="grid_view">Quadrant Assignment</SectionTitle>
            <p className="text-xs text-on-surface-variant mb-3">
              Quadrants are determined by the <strong>4 / 3 threshold</strong>: Impact ≥ 4 or Feasibility ≥ 4 = "high".
            </p>
            <ScoreTable
              headers={["Quadrant", "Impact", "Feasibility", "Action"]}
              rows={[
                [<QuadrantChip label="Quick Win" />,     "4 – 5", "4 – 5", "Do first"],
                [<QuadrantChip label="Major Project" />, "4 – 5", "1 – 3", "Plan & resource"],
                [<QuadrantChip label="Fill In" />,       "1 – 3", "4 – 5", "Nice to have"],
                [<QuadrantChip label="Reconsider" />,    "1 – 3", "1 – 3", "Deprioritise"],
                [<QuadrantChip label="Needs Input" />,   "—",     "—",     "Fill time_spent_hrs"],
              ]}
            />
          </section>

          <hr className="border-outline-variant/20" />

          {/* Example rows */}
          <section>
            <SectionTitle icon="table_rows">Example Records</SectionTitle>
            <div className="space-y-2">
              {[
                { name: "Manual invoice matching", hours: 60, feasibility: "High",   impact: 5, fScore: 5, priority: 25, q: "Quick Win" },
                { name: "Monthly board report",   hours: 15, feasibility: "Low",    impact: 4, fScore: 1, priority: 4,  q: "Major Project" },
                { name: "Ad-hoc data queries",    hours: 3,  feasibility: "High",   impact: 2, fScore: 5, priority: 10, q: "Fill In" },
                { name: "Coffee machine logs",    hours: 1,  feasibility: "Medium", impact: 2, fScore: 3, priority: 6,  q: "Reconsider" },
                { name: "Unknown process",        hours: null,feasibility: "High",  impact: null, fScore: 5, priority: null, q: "Needs Input" },
              ].map((ex, i) => (
                <div key={i} className="rounded-lg border border-outline-variant/20 p-3 flex items-center gap-3 bg-surface-container-lowest/50">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold text-on-surface truncate">{ex.name}</p>
                    <p className="text-xs text-on-surface-variant">
                      {ex.hours != null ? `${ex.hours} hrs/mo · ` : "No time data · "}
                      Feasibility: {ex.feasibility}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0 text-xs text-on-surface-variant">
                    <span title="Impact">I: <strong className="text-on-surface">{ex.impact ?? "—"}</strong></span>
                    <span>×</span>
                    <span title="Feasibility">F: <strong className="text-on-surface">{ex.fScore}</strong></span>
                    <span>=</span>
                    <strong className="text-on-surface">{ex.priority ?? "—"}</strong>
                    <QuadrantChip label={ex.q} />
                  </div>
                </div>
              ))}
            </div>
          </section>

          <hr className="border-outline-variant/20" />

          {/* Tweak note */}
          <section className="rounded-xl border border-primary/20 bg-primary/5 p-4">
            <div className="flex gap-3">
              <span className="material-symbols-outlined text-primary text-[20px] mt-0.5">info</span>
              <div>
                <p className="text-xs font-bold text-on-surface mb-1">All scoring is formula-driven</p>
                <p className="text-xs text-on-surface-variant">
                  Scores update automatically when records are edited. The threshold logic (4 = "high") 
                  can be adjusted in <code className="bg-surface-container px-1 rounded text-[11px]">scoring.py</code> and will 
                  propagate across the entire portfolio instantly.
                </p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

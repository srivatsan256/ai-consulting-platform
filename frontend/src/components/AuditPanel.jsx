import React, { useState, useEffect } from "react";
import { painAreaService, getApiError } from "../services/api";

/* ──────────────────────────────────────────────────────────────
   Audit Panel
   Fetches the /audit/ endpoint and displays a structured data-
   quality report: column inventory, gap analysis, quadrant
   distribution, flagged rows, and a meeting-ready executive
   summary.
   ────────────────────────────────────────────────────────────── */

const QUADRANT_STYLE = {
  "Quick Win":     { bg: "bg-emerald-100", text: "text-emerald-700", dot: "bg-emerald-500" },
  "Strategic":     { bg: "bg-blue-100",    text: "text-blue-700",    dot: "bg-blue-500" },
  "Fill In":       { bg: "bg-amber-100",   text: "text-amber-700",   dot: "bg-amber-500" },
  "Revisit":       { bg: "bg-red-100",     text: "text-red-700",     dot: "bg-red-500" },
  "Needs Input":   { bg: "bg-slate-100",   text: "text-slate-500",   dot: "bg-slate-400" },
};

function QuadrantCount({ label, count }) {
  const s = QUADRANT_STYLE[label] || QUADRANT_STYLE["Needs Input"];
  return (
    <div className={`rounded-xl p-3 flex items-center justify-between gap-2 ${s.bg}`}>
      <span className={`flex items-center gap-1.5 text-xs font-semibold ${s.text}`}>
        <span className={`w-2 h-2 rounded-full ${s.dot}`} />
        {label}
      </span>
      <span className={`text-lg font-bold ${s.text}`}>{count}</span>
    </div>
  );
}

function FieldRow({ field, filled, missing, total }) {
  const pct = total ? Math.round((filled / total) * 100) : 0;
  const isCritical = ["time_spent_hrs", "priority", "feasibility"].includes(field);
  return (
    <div className="flex items-center gap-3 py-2 border-b border-outline-variant/10 last:border-0">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5 mb-1">
          {isCritical && (
            <span className="w-1.5 h-1.5 rounded-full bg-primary" title="Critical scoring field" />
          )}
          <span className="text-xs font-mono text-on-surface">{field.replace(/_/g, " ")}</span>
          {isCritical && (
            <span className="text-[10px] font-bold text-primary bg-primary/10 px-1.5 rounded-full">scoring</span>
          )}
        </div>
        <div className="h-1.5 bg-outline-variant/20 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${pct < 50 ? "bg-error" : pct < 80 ? "bg-warning" : "bg-success"}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
      <div className="text-right shrink-0">
        <p className="text-xs font-bold text-on-surface">{pct}%</p>
        <p className="text-[10px] text-on-surface-variant">{filled}/{total}</p>
      </div>
      {missing > 0 && (
        <span className="text-xs font-semibold text-error bg-error/10 px-2 py-0.5 rounded-lg shrink-0">
          {missing} missing
        </span>
      )}
    </div>
  );
}

export default function AuditPanel({ onClose }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [flaggedExpanded, setFlaggedExpanded] = useState(false);

  useEffect(() => {
    painAreaService
      .audit()
      .then((res) => setData(res.data))
      .catch((err) => setError(getApiError(err)))
      .finally(() => setLoading(false));
  }, []);

  const total = data?.total_records ?? 0;
  const needsInputPct = data?.needs_input_pct ?? 0;
  const showBlockerBanner = needsInputPct > 50;

  return (
    <div
      className="fixed inset-0 z-50 flex justify-end"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="absolute inset-0 bg-black/30 backdrop-blur-[2px]" onClick={onClose} />

      <div className="relative z-10 w-full max-w-xl bg-white h-full shadow-2xl flex flex-col overflow-hidden animate-slide-in-right">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-outline-variant/20 bg-gradient-to-r from-amber-50 to-transparent flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-amber-100 flex items-center justify-center">
              <span className="material-symbols-outlined text-amber-600 text-[20px]">search_check</span>
            </div>
            <div>
              <h2 className="text-base font-bold text-on-surface">Data Audit</h2>
              <p className="text-xs text-on-surface-variant">Part 1 of the Scoring Matrix Framework</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-surface-container transition-colors text-on-surface-variant"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-6 py-5 space-y-6">
          {loading && (
            <div className="flex items-center justify-center h-40 gap-3 text-on-surface-variant">
              <span className="material-symbols-outlined animate-spin text-primary">progress_activity</span>
              <span className="text-sm">Running audit…</span>
            </div>
          )}

          {error && (
            <div className="rounded-xl border border-error/20 bg-error/5 p-4 flex gap-3">
              <span className="material-symbols-outlined text-error text-[20px]">error</span>
              <p className="text-sm text-error">{error}</p>
            </div>
          )}

          {data && (
            <>
              {/* Executive Summary */}
              <section>
                <div className="flex items-center gap-2 mb-3">
                  <span className="material-symbols-outlined text-primary text-[20px]">summarize</span>
                  <h3 className="text-sm font-bold text-on-surface">Executive Summary</h3>
                </div>
                <div className="rounded-xl border border-primary/20 bg-gradient-to-br from-primary/5 to-transparent p-4">
                  <p className="text-sm text-on-surface leading-relaxed">{data.executive_summary}</p>
                </div>
              </section>

              {/* Primary Blocker Banner */}
              {showBlockerBanner && data.primary_blocker && (
                <div className="rounded-xl border border-error/30 bg-error/5 p-4 flex gap-3">
                  <span className="material-symbols-outlined text-error text-[20px] mt-0.5 shrink-0">warning</span>
                  <div>
                    <p className="text-xs font-bold text-error mb-0.5">Primary Blocker</p>
                    <p className="text-xs text-on-surface">{data.primary_blocker}</p>
                  </div>
                </div>
              )}

              {/* Quadrant Distribution */}
              <section>
                <div className="flex items-center gap-2 mb-3">
                  <span className="material-symbols-outlined text-primary text-[20px]">grid_view</span>
                  <h3 className="text-sm font-bold text-on-surface">Prioritization Summary</h3>
                  <span className="ml-auto text-xs text-on-surface-variant">{total} total</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(data.quadrant_distribution).map(([label, count]) => (
                    <QuadrantCount key={label} label={label} count={count} />
                  ))}
                </div>
                <div className="mt-2 flex justify-between text-xs text-on-surface-variant px-1">
                  <span>Needs Input rate</span>
                  <span className={`font-bold ${showBlockerBanner ? "text-error" : "text-success"}`}>
                    {needsInputPct}%
                  </span>
                </div>
              </section>

              {/* Column Inventory */}
              <section>
                <div className="flex items-center gap-2 mb-3">
                  <span className="material-symbols-outlined text-primary text-[20px]">table_view</span>
                  <h3 className="text-sm font-bold text-on-surface">Column Inventory</h3>
                </div>
                <div className="rounded-xl border border-outline-variant/20 bg-surface-container-lowest p-4">
                  {data.column_inventory.map((col) => (
                    <FieldRow
                      key={col.field}
                      field={col.field}
                      filled={col.filled}
                      missing={col.missing}
                      total={total}
                    />
                  ))}
                  <p className="mt-2 text-[10px] text-on-surface-variant">
                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-primary mr-1" />
                    Blue dot = critical scoring field (drives Impact / Feasibility score)
                  </p>
                </div>
              </section>

              {/* Flagged Rows */}
              {data.flagged_rows?.length > 0 && (
                <section>
                  <button
                    onClick={() => setFlaggedExpanded((p) => !p)}
                    className="flex items-center justify-between w-full text-left"
                  >
                    <div className="flex items-center gap-2">
                      <span className="material-symbols-outlined text-amber-600 text-[20px]">flag</span>
                      <h3 className="text-sm font-bold text-on-surface">
                        Flagged Rows
                        <span className="ml-2 text-xs font-normal text-on-surface-variant">
                          ({data.flagged_rows.length} records with missing critical fields)
                        </span>
                      </h3>
                    </div>
                    <span className="material-symbols-outlined text-on-surface-variant text-[18px]">
                      {flaggedExpanded ? "expand_less" : "expand_more"}
                    </span>
                  </button>

                  {flaggedExpanded && (
                    <div className="mt-3 space-y-1 max-h-60 overflow-y-auto pr-1">
                      {data.flagged_rows.map((row) => (
                        <div
                          key={row.id}
                          className="flex items-start gap-3 rounded-lg border border-amber-100 bg-amber-50 px-3 py-2"
                        >
                          <span className="material-symbols-outlined text-amber-500 text-[16px] mt-0.5">warning_amber</span>
                          <div className="min-w-0">
                            <p className="text-xs font-semibold text-on-surface truncate">
                              #{row.id} · {row.process_activity}
                            </p>
                            <p className="text-[10px] text-on-surface-variant">
                              Missing: {row.missing_fields.join(", ")}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </section>
              )}

              {/* Methodology Note */}
              <section className="rounded-xl border border-outline-variant/20 bg-surface-container-lowest p-4">
                <p className="text-xs font-bold text-on-surface mb-2">Scoring Assumptions</p>
                <ul className="space-y-1 text-xs text-on-surface-variant list-disc list-inside">
                  <li><strong>Impact Score</strong> = Time Spent / Month banding (1–5 scale, 5 bands)</li>
                  <li><strong>Feasibility Score</strong> = Feasibility field High/Medium/Low → 5/3/1</li>
                  <li><strong>Priority Score</strong> = Impact × Feasibility (max 25)</li>
                  <li><strong>Quadrant</strong> = Impact ≥ 4 + Feasibility ≥ 4 → Quick Win, etc.</li>
                  <li>All scoring is formula-driven — adjustable in <code className="bg-surface-container px-1 rounded">scoring.py</code></li>
                </ul>
              </section>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

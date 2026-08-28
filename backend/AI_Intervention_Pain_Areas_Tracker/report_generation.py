"""Executive report generation (Phase 5) for the AI Intervention Pain Areas
Tracker.

Produces five report types, each exportable as PDF (reportlab) or Excel
(openpyxl):

* opportunity-assessment - AI Opportunity Assessment Report
* department-summary    - Department Summary
* executive-summary     - Executive Summary
* adoption-roadmap      - AI Adoption Roadmap
* opportunity-register  - Opportunity Register
"""

import datetime
import io

from .scoring import score_from_priority, score_from_time_spent, quadrant_from_scores
from .recommendations import recommend, AI_SOLUTIONS

REPORT_TYPES = {
    "opportunity-assessment": {
        "title": "AI Opportunity Assessment Report",
        "description": (
            "Full assessment of AI opportunities across the organisation, "
            "including scoring, recommendations and confidence."
        ),
    },
    "department-summary": {
        "title": "Department Summary",
        "description": (
            "Where AI effort is concentrated by department - opportunities, "
            "hours and recommended solutions."
        ),
    },
    "executive-summary": {
        "title": "Executive Summary",
        "description": (
            "A one-page overview for leadership with headline KPIs and the "
            "top opportunities."
        ),
    },
    "adoption-roadmap": {
        "title": "AI Adoption Roadmap",
        "description": (
            "A phased plan to turn opportunities into live AI initiatives."
        ),
    },
    "opportunity-register": {
        "title": "Opportunity Register",
        "description": (
            "The complete register of every tracked opportunity with its AI "
            "recommendation and confidence."
        ),
    },
}

SOLUTION_ORDER = [s["name"] for s in AI_SOLUTIONS]

_PRIORITY_LABEL = {"High": "high", "Medium": "medium", "Low": "low"}


def _num(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_sum(*values):
    return sum(_num(v) for v in values)


def _fmt_hours(value):
    return f"{_num(value):g}"


def _recommendation_for(record):
    rec = recommend(record)
    return {
        "name": rec["name"],
        "key": rec["key"],
        "icon": rec["icon"],
        "confidence": rec["confidence"],
        "reasoning": rec["reasoning"],
    }


def _register_row(record, rec):
    time_score = score_from_time_spent(record.time_spent_hrs)
    feas_score = score_from_priority(record.feasibility)
    prio_score = score_from_priority(record.priority)
    return {
        "date": record.date,
        "department": record.department or "",
        "process_activity": record.process_activity or "",
        "pain_area": record.pain_area or "",
        "time_spent_hrs": record.time_spent_hrs,
        "impact_score": time_score,
        "feasibility_score": feas_score,
        "priority_score": prio_score,
        "total_score": _safe_sum(time_score, feas_score, prio_score),
        "quadrant": quadrant_from_scores(time_score, feas_score),
        "priority": record.priority or "",
        "feasibility": record.feasibility or "",
        "status": record.status or "",
        "owner": record.owner or "",
        "target_date": record.target_date,
        "ai_intervention": record.ai_intervention or "",
        "ai_recommendation": rec["name"],
        "ai_confidence": rec["confidence"],
    }


def build_report_data(records):
    """Compute every number used across the five reports."""
    rows = [_register_row(r, _recommendation_for(r)) for r in records]
    rows.sort(key=lambda r: -r["total_score"])

    total_hours = sum(_num(r.time_spent_hrs) for r in records)
    scored = [r for r in records if r.time_spent_hrs is not None]
    avg_impact = (
        sum(score_from_time_spent(r.time_spent_hrs) for r in scored) / len(scored) # type: ignore
        if scored
        else 0
    )

    quadrant_counts = {"Quick Win": 0, "Strategic": 0, "Fill In": 0, "Revisit": 0}
    for r in rows:
        q = r["quadrant"]
        if q in quadrant_counts:
            quadrant_counts[q] += 1

    solution_dist = {}
    for name in SOLUTION_ORDER:
        solution_dist[name] = 0
    for r in rows:
        solution_dist[r["ai_recommendation"]] = (
            solution_dist.get(r["ai_recommendation"], 0) + 1
        )

    dept_map = {}
    for r in rows:
        dept = r["department"] or "Unknown"
        entry = dept_map.setdefault(
            dept,
            {
                "department": dept,
                "opportunities": 0,
                "hours": 0.0,
                "score_sum": 0,
                "quick_wins": 0,
                "solutions": {},
            },
        )
        entry["opportunities"] += 1
        entry["hours"] += _num(r["time_spent_hrs"])
        entry["score_sum"] += r["total_score"]
        if r["quadrant"] == "Quick Win":
            entry["quick_wins"] += 1
        entry["solutions"][r["ai_recommendation"]] = (
            entry["solutions"].get(r["ai_recommendation"], 0) + 1
        )

    department_summary = []
    for entry in sorted(dept_map.values(), key=lambda d: -d["opportunities"]):
        top_solution = max(
            entry["solutions"].items(), key=lambda kv: kv[1], default=("", 0)
        )[0]
        department_summary.append(
            {
                "department": entry["department"],
                "opportunities": entry["opportunities"],
                "hours": round(entry["hours"]),
                "avg_score": (
                    round(entry["score_sum"] / entry["opportunities"], 1)
                    if entry["opportunities"]
                    else 0
                ),
                "quick_wins": entry["quick_wins"],
                "top_solution": top_solution,
            }
        )

    leaderboard = rows[:10]

    roadmap = _build_roadmap(rows, quadrant_counts)

    return {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "report_count": len(rows),
        "total_hours": round(total_hours),
        "departments": len(department_summary),
        "open_count": sum(1 for r in rows if r["status"] == "Open"),
        "avg_impact": round(avg_impact, 1),
        "avg_priority": round(
            sum(_num(r["priority_score"]) for r in rows) / len(rows) if rows else 0, 1
        ),
        "quadrant_counts": quadrant_counts,
        "solution_distribution": [
            {"name": name, "count": solution_dist.get(name, 0)}
            for name in SOLUTION_ORDER
        ],
        "leaderboard": leaderboard,
        "department_summary": department_summary,
        "roadmap": roadmap,
        "register": rows,
    }


def _build_roadmap(rows, quadrant_counts):
    quick_wins = [r for r in rows if r["quadrant"] == "Quick Win"]
    strategic = [r for r in rows if r["quadrant"] == "Strategic"]
    long_term = [r for r in rows if r["quadrant"] in ("Fill In", "Revisit")]

    def sort_key(r):
        return -r["total_score"]

    return {
        "phase_1": {
            "title": "Phase 1 - Quick Wins",
            "timeframe": "Months 0-3",
            "focus": "Deploy high-feasibility solutions that deliver value fast.",
            "count": len(quick_wins),
            "items": sorted(quick_wins, key=sort_key),
        },
        "phase_2": {
            "title": "Phase 2 - Strategic Initiatives",
            "timeframe": "Months 3-6",
            "focus": "Tackle high-impact, harder-to-build initiatives with strong sponsorship.",
            "count": len(strategic),
            "items": sorted(strategic, key=sort_key),
        },
        "phase_3": {
            "title": "Phase 3 - Scale & Fill-In",
            "timeframe": "Months 6-12",
            "focus": "Scale proven solutions and revisit lower-scoring opportunities.",
            "count": len(long_term),
            "items": sorted(long_term, key=sort_key),
        },
    }


# ---------------------------------------------------------------------------
# Excel export
# ---------------------------------------------------------------------------

from openpyxl import Workbook  # noqa: E402
from openpyxl.styles import Alignment, Font, PatternFill  # noqa: E402
from openpyxl.utils import get_column_letter  # noqa: E402

_HEADER_FILL = PatternFill("solid", fgColor="0D9488")
_HEADER_FONT = Font(bold=True, color="FFFFFF")
_TITLE_FONT = Font(bold=True, size=14, color="0F172A")
_SUB_FONT = Font(size=10, color="64748B")
_WRAP = Alignment(wrap_text=True, vertical="top")


def _sheet_title(ws, title, subtitle):
    ws.append([title])
    ws.cell(ws.max_row, 1).font = _TITLE_FONT
    ws.append([subtitle])
    ws.cell(ws.max_row, 1).font = _SUB_FONT
    ws.append([])


def _write_table(ws, headers, rows, widths=None, start_row=None):
    if start_row is None:
        start_row = ws.max_row + 1
    header_row = start_row
    ws.append(headers)
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(header_row, col_idx)
        cell.fill = _HEADER_FILL
        cell.font = _HEADER_FONT
        cell.alignment = Alignment(vertical="center")
    for row in rows:
        ws.append(row)
        for col_idx in range(1, len(headers) + 1):
            ws.cell(ws.max_row, col_idx).alignment = _WRAP
    if widths:
        for idx, width in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(idx)].width = width


def _render_xlsx(report_type, records, data):
    wb = Workbook()
    default_sheet = wb.active
    default_sheet.title = report_type # type: ignore

    _sheet_title(
        default_sheet,
        REPORT_TYPES[report_type]["title"],
        f"Generated {data['generated_at'].replace('T', ' ')}  |  "
        f"{data['report_count']} opportunities  |  "
        f"{data['total_hours']} hrs/month",
    )

    if report_type == "opportunity-assessment":
        _assessment_sheets(wb, data)
    elif report_type == "department-summary":
        _department_sheets(wb, data)
    elif report_type == "executive-summary":
        _executive_sheets(wb, data)
    elif report_type == "adoption-roadmap":
        _roadmap_sheets(wb, data)
    else:  # opportunity-register
        _register_sheets(wb, data)

    stream = io.BytesIO()
    wb.save(stream)
    return stream.getvalue()


def _assessment_sheets(wb, data):
    ws = wb.active
    ws.title = "Overview"
    _sheet_title(ws, "AI Opportunity Assessment Report", data["generated_at"])
    _write_table(
        ws,
        ["Metric", "Value"],
        [
            ["Total opportunities", data["report_count"]],
            ["Total hours / month", data["total_hours"]],
            ["Departments covered", data["departments"]],
            ["Open opportunities", data["open_count"]],
            ["Avg impact score (of 3)", data["avg_impact"]],
            ["Avg priority score (of 3)", data["avg_priority"]],
            ["Quick wins", data["quadrant_counts"]["Quick Win"]],
            ["Strategic", data["quadrant_counts"]["Strategic"]],
            ["Fill In", data["quadrant_counts"]["Fill In"]],
            ["Revisit", data["quadrant_counts"]["Revisit"]],
        ],
        widths=[32, 16],
    )
    _write_table(
        ws,
        ["AI Solution", "Opportunities"],
        [[d["name"], d["count"]] for d in data["solution_distribution"]],
        widths=[32, 16],
    )
    _write_table(
        ws,
        [
            "Rank",
            "Department",
            "Process / Activity",
            "Total Score",
            "Quadrant",
            "AI Recommendation",
            "Confidence",
            "Reasoning",
        ],
        [
            [
                i + 1,
                r["department"],
                r["process_activity"],
                r["total_score"],
                r["quadrant"],
                r["ai_recommendation"],
                f"{r['ai_confidence']}%",
                r.get("reasoning", ""),
            ]
            for i, r in enumerate(data["leaderboard"])
        ],
        widths=[8, 18, 30, 12, 14, 26, 12, 70],
    )


def _department_sheets(wb, data):
    ws = wb.active
    ws.title = "Department Summary"
    _sheet_title(ws, "Department Summary", data["generated_at"])
    _write_table(
        ws,
        [
            "Department",
            "Opportunities",
            "Hours / Month",
            "Avg Score",
            "Quick Wins",
            "Top AI Solution",
        ],
        [
            [
                d["department"],
                d["opportunities"],
                d["hours"],
                d["avg_score"],
                d["quick_wins"],
                d["top_solution"],
            ]
            for d in data["department_summary"]
        ],
        widths=[26, 16, 14, 12, 12, 30],
    )
    _write_table(
        ws,
        ["AI Solution", "Opportunities"],
        [[d["name"], d["count"]] for d in data["solution_distribution"]],
        widths=[32, 16],
    )


def _executive_sheets(wb, data):
    ws = wb.active
    ws.title = "Executive Summary"
    _sheet_title(ws, "Executive Summary", data["generated_at"])
    _write_table(
        ws,
        ["Metric", "Value"],
        [
            ["AI opportunities identified", data["report_count"]],
            ["Monthly hours consumed today", data["total_hours"]],
            ["Departments with opportunities", data["departments"]],
            ["Quick wins ready to start", data["quadrant_counts"]["Quick Win"]],
            ["Strategic initiatives", data["quadrant_counts"]["Strategic"]],
            ["Avg impact score (of 3)", data["avg_impact"]],
        ],
        widths=[34, 18],
    )
    _write_table(
        ws,
        ["AI Solution", "Opportunities"],
        [[d["name"], d["count"]] for d in data["solution_distribution"]],
        widths=[32, 16],
    )
    _write_table(
        ws,
        [
            "Rank",
            "Department",
            "Process / Activity",
            "Score",
            "Quadrant",
            "AI Recommendation",
            "Confidence",
        ],
        [
            [
                i + 1,
                r["department"],
                r["process_activity"],
                r["total_score"],
                r["quadrant"],
                r["ai_recommendation"],
                f"{r['ai_confidence']}%",
            ]
            for i, r in enumerate(data["leaderboard"][:5])
        ],
        widths=[8, 20, 34, 10, 14, 26, 12],
    )


def _roadmap_sheets(wb, data):
    ws = wb.active
    ws.title = "Adoption Roadmap"
    _sheet_title(ws, "AI Adoption Roadmap", data["generated_at"])
    for phase_key, phase in data["roadmap"].items():
        _write_table(
            ws,
            [f"{phase['title']} ({phase['timeframe']})"],
            [[phase["focus"]]],
            widths=[60],
        )
        _write_table(
            ws,
            ["Process / Activity", "Department", "Score", "Quadrant", "AI Recommendation", "Confidence"],
            [
                [
                    r["process_activity"],
                    r["department"],
                    r["total_score"],
                    r["quadrant"],
                    r["ai_recommendation"],
                    f"{r['ai_confidence']}%",
                ]
                for r in phase["items"]
            ],
            widths=[40, 20, 10, 14, 26, 12],
        )
        ws.append([])


def _register_sheets(wb, data):
    ws = wb.active
    ws.title = "Opportunity Register"
    _sheet_title(ws, "Opportunity Register", data["generated_at"])
    _write_table(
        ws,
        [
            "Date",
            "Department",
            "Process / Activity",
            "Pain Area",
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
            "AI Recommendation",
            "Confidence",
        ],
        [
            [
                r["date"],
                r["department"],
                r["process_activity"],
                r["pain_area"],
                _fmt_hours(r["time_spent_hrs"]),
                r["impact_score"],
                r["feasibility_score"],
                r["priority_score"],
                r["total_score"],
                r["quadrant"],
                r["priority"],
                r["status"],
                r["owner"],
                r["target_date"],
                r["ai_intervention"],
                r["ai_recommendation"],
                f"{r['ai_confidence']}%",
            ]
            for r in data["register"]
        ],
        widths=[12, 18, 30, 40, 10, 9, 11, 9, 9, 14, 10, 12, 16, 12, 40, 26, 12],
    )


# ---------------------------------------------------------------------------
# PDF export
# ---------------------------------------------------------------------------

from reportlab.lib import colors  # type: ignore # noqa: E402
from reportlab.lib.enums import TA_CENTER, TA_LEFT  # type: ignore # noqa: E402
from reportlab.lib.pagesizes import A4  # type: ignore # noqa: E402
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # type: ignore # noqa: E402
from reportlab.lib.units import inch, mm  # type: ignore # noqa: E402
from reportlab.platypus import (  # noqa: E402 # type: ignore
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

_TEAL = colors.HexColor("#0D9488")
_SLATE = colors.HexColor("#334155")
_LIGHT = colors.HexColor("#F1F5F9")


def _escape(text):
    return (
        str(text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleX",
            parent=base["Title"],
            fontSize=18,
            textColor=_SLATE,
            spaceAfter=2,
        ),
        "subtitle": ParagraphStyle(
            "SubtitleX",
            parent=base["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "H2X",
            parent=base["Heading2"],
            fontSize=13,
            textColor=_TEAL,
            spaceBefore=14,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "BodyX",
            parent=base["BodyText"],
            fontSize=9.5,
            leading=13,
            textColor=_SLATE,
            spaceAfter=4,
        ),
        "body_bold": ParagraphStyle(
            "BodyBoldX",
            parent=base["BodyText"],
            fontSize=9.5,
            leading=13,
            textColor=_SLATE,
            fontName="Helvetica-Bold",
        ),
        "cell": ParagraphStyle(
            "CellX",
            parent=base["BodyText"],
            fontSize=8,
            leading=10.5,
            textColor=_SLATE,
        ),
        "cell_bold": ParagraphStyle(
            "CellBoldX",
            parent=base["BodyText"],
            fontSize=8,
            leading=10.5,
            textColor=_SLATE,
            fontName="Helvetica-Bold",
        ),
        "center": ParagraphStyle(
            "CenterX",
            parent=base["BodyText"],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=_SLATE,
        ),
    }


def _tbl(headers, rows, widths, styles):
    head = [Paragraph(_escape(h), styles["cell_bold"]) for h in headers]
    body = [
        [Paragraph(_escape(str(c or "")), styles["cell"]) for c in row]
        for row in rows
    ]
    table = Table([head, *body], colWidths=widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _TEAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _LIGHT]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def _render_pdf(report_type, records, data):
    styles = _build_styles()
    stream = io.BytesIO()
    doc = SimpleDocTemplate(
        stream,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title=REPORT_TYPES[report_type]["title"],
    )
    story = [Paragraph(_escape(REPORT_TYPES[report_type]["title"]), styles["title"])]
    story.append(
        Paragraph(
            f"AI Consulting Platform  ·  Generated {data['generated_at'].replace('T', ' ')}",
            styles["subtitle"],
        )
    )

    full_width = A4[0] - 28 * mm

    if report_type == "opportunity-assessment":
        story += _pdf_assessment(data, styles, full_width)
    elif report_type == "department-summary":
        story += _pdf_department(data, styles, full_width)
    elif report_type == "executive-summary":
        story += _pdf_executive(data, styles, full_width)
    elif report_type == "adoption-roadmap":
        story += _pdf_roadmap(data, styles, full_width)
    else:  # opportunity-register
        story += _pdf_register(data, styles, full_width)

    doc.build(story) # type: ignore
    return stream.getvalue()


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

import csv  # noqa: E402


def _csv_row(value):
    """Format a single value for CSV output."""
    if value is None:
        return ""
    return str(value)


def _sanitize_csv_value(value):
    """Sanitize a value to prevent CSV injection in spreadsheet apps.

    Cells starting with =, +, -, @, \\t, or \\r are prefixed with a single
    quote to neutralise formula interpretation.
    """
    s = str(value) if value is not None else ""
    if s and s[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + s
    return s


def _render_csv(report_type, records, data):
    """Render a report as CSV and return bytes (with BOM for Excel compat)."""
    stream = io.StringIO()
    writer = csv.writer(stream, quoting=csv.QUOTE_MINIMAL)

    if report_type == "opportunity-assessment":
        _csv_assessment(writer, data)
    elif report_type == "department-summary":
        _csv_department(writer, data)
    elif report_type == "executive-summary":
        _csv_executive(writer, data)
    elif report_type == "adoption-roadmap":
        _csv_roadmap(writer, data)
    else:  # opportunity-register
        _csv_register(writer, data)

    return ("\ufeff" + stream.getvalue()).encode("utf-8")


def _csv_assessment(writer, data):
    writer.writerow(["AI Opportunity Assessment Report"])
    writer.writerow([f"Generated: {data['generated_at']}"])
    writer.writerow([])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Total opportunities", data["report_count"]])
    writer.writerow(["Total hours / month", data["total_hours"]])
    writer.writerow(["Departments covered", data["departments"]])
    writer.writerow(["Open opportunities", data["open_count"]])
    writer.writerow(["Avg impact score (of 3)", data["avg_impact"]])
    writer.writerow(["Avg priority score (of 3)", data["avg_priority"]])
    writer.writerow(["Quick wins", data["quadrant_counts"]["Quick Win"]])
    writer.writerow(["Strategic", data["quadrant_counts"]["Strategic"]])
    writer.writerow(["Fill In", data["quadrant_counts"]["Fill In"]])
    writer.writerow(["Revisit", data["quadrant_counts"]["Revisit"]])
    writer.writerow([])
    writer.writerow(["AI Solution", "Opportunities"])
    for item in data["solution_distribution"]:
        writer.writerow([item["name"], item["count"]])
    writer.writerow([])
    writer.writerow(["Rank", "Department", "Process / Activity", "Total Score", "Quadrant", "AI Recommendation", "Confidence", "Reasoning"])
    if not data["leaderboard"]:
        writer.writerow(["No data available"])
        return
    for i, r in enumerate(data["leaderboard"]):
        writer.writerow([
            i + 1,
            _sanitize_csv_value(r["department"]),
            _sanitize_csv_value(r["process_activity"]),
            r["total_score"],
            r["quadrant"],
            _sanitize_csv_value(r["ai_recommendation"]),
            f"{r['ai_confidence']}%",
            _sanitize_csv_value(r.get("reasoning", "")),
        ])


def _csv_department(writer, data):
    writer.writerow(["Department Summary"])
    writer.writerow([f"Generated: {data['generated_at']}"])
    writer.writerow([])
    writer.writerow(["Department", "Opportunities", "Hours / Month", "Avg Score", "Quick Wins", "Top AI Solution"])
    if not data["department_summary"]:
        writer.writerow(["No data available"])
    else:
        for d in data["department_summary"]:
            writer.writerow([
                _sanitize_csv_value(d["department"]),
                d["opportunities"],
                d["hours"],
                d["avg_score"],
                d["quick_wins"],
                _sanitize_csv_value(d["top_solution"]),
            ])
    writer.writerow([])
    writer.writerow(["AI Solution", "Opportunities"])
    for item in data["solution_distribution"]:
        writer.writerow([item["name"], item["count"]])


def _csv_executive(writer, data):
    writer.writerow(["Executive Summary"])
    writer.writerow([f"Generated: {data['generated_at']}"])
    writer.writerow([])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["AI opportunities identified", data["report_count"]])
    writer.writerow(["Monthly hours consumed today", data["total_hours"]])
    writer.writerow(["Departments with opportunities", data["departments"]])
    writer.writerow(["Quick wins ready to start", data["quadrant_counts"]["Quick Win"]])
    writer.writerow(["Strategic initiatives", data["quadrant_counts"]["Strategic"]])
    writer.writerow(["Avg impact score (of 3)", data["avg_impact"]])
    writer.writerow([])
    writer.writerow(["AI Solution", "Opportunities"])
    for item in data["solution_distribution"]:
        writer.writerow([item["name"], item["count"]])
    writer.writerow([])
    writer.writerow(["Rank", "Department", "Process / Activity", "Score", "Quadrant", "AI Recommendation", "Confidence"])
    if not data["leaderboard"]:
        writer.writerow(["No data available"])
        return
    for i, r in enumerate(data["leaderboard"][:5]):
        writer.writerow([
            i + 1,
            _sanitize_csv_value(r["department"]),
            _sanitize_csv_value(r["process_activity"]),
            r["total_score"],
            r["quadrant"],
            _sanitize_csv_value(r["ai_recommendation"]),
            f"{r['ai_confidence']}%",
        ])


def _csv_roadmap(writer, data):
    writer.writerow(["AI Adoption Roadmap"])
    writer.writerow([f"Generated: {data['generated_at']}"])
    writer.writerow([])
    for phase_key, phase in data["roadmap"].items():
        writer.writerow([f"{phase['title']} ({phase['timeframe']})"])
        writer.writerow([phase["focus"]])
        writer.writerow(["Process / Activity", "Department", "Score", "Quadrant", "AI Recommendation", "Confidence"])
        if not phase["items"]:
            writer.writerow(["No opportunities in this phase"])
        else:
            for r in phase["items"]:
                writer.writerow([
                    _sanitize_csv_value(r["process_activity"]),
                    _sanitize_csv_value(r["department"]),
                    r["total_score"],
                    r["quadrant"],
                    _sanitize_csv_value(r["ai_recommendation"]),
                    f"{r['ai_confidence']}%",
                ])
        writer.writerow([])


def _csv_register(writer, data):
    writer.writerow(["Opportunity Register"])
    writer.writerow([f"Generated: {data['generated_at']}"])
    writer.writerow([])
    writer.writerow([
        "Date", "Department", "Process / Activity", "Pain Area", "Hours",
        "Impact Score", "Feasibility Score", "Priority Score", "Total Score", "Quadrant",
        "Priority", "Status", "Owner", "Target Date", "AI Intervention",
        "AI Recommendation", "Confidence",
    ])
    if not data["register"]:
        writer.writerow(["No data available"])
        return
    for r in data["register"]:
        writer.writerow([
            r["date"],
            _sanitize_csv_value(r["department"]),
            _sanitize_csv_value(r["process_activity"]),
            _sanitize_csv_value(r["pain_area"]),
            _fmt_hours(r["time_spent_hrs"]),
            r["impact_score"],
            r["feasibility_score"],
            r["priority_score"],
            r["total_score"],
            r["quadrant"],
            r["priority"],
            r["status"],
            _sanitize_csv_value(r["owner"]),
            r["target_date"],
            _sanitize_csv_value(r["ai_intervention"]),
            _sanitize_csv_value(r["ai_recommendation"]),
            f"{r['ai_confidence']}%",
        ])


def _pdf_assessment(data, styles, width):
    story = [
        Paragraph("Overview", styles["h2"]),
        _tbl(
            ["Metric", "Value"],
            [
                ["Total opportunities", data["report_count"]],
                ["Total hours / month", data["total_hours"]],
                ["Departments covered", data["departments"]],
                ["Open opportunities", data["open_count"]],
                ["Quick wins / strategic / fill-in / revisit", (
                    f"{data['quadrant_counts']['Quick Win']} / "
                    f"{data['quadrant_counts']['Strategic']} / "
                    f"{data['quadrant_counts']['Fill In']} / "
                    f"{data['quadrant_counts']['Revisit']}"
                )],
            ],
            [width * 0.55, width * 0.45],
            styles,
        ),
        Paragraph("Recommended AI Solutions", styles["h2"]),
        _tbl(
            ["AI Solution", "Opportunities", "Share"],
            [
                [name, d["count"], f"{round(d['count'] / max(1, data['report_count']) * 100)}%"]
                for name, d in [
                    (item["name"], item) for item in data["solution_distribution"]
                ]
            ],
            [width * 0.6, width * 0.2, width * 0.2],
            styles,
        ),
    ]
    if data["leaderboard"]:
        story.append(Paragraph("Top AI Opportunities", styles["h2"]))
        story.append(
            _tbl(
                ["Rank", "Department", "Process / Activity", "Score", "Quadrant", "AI Recommendation", "Confidence"],
                [
                    [
                        i + 1,
                        r["department"],
                        r["process_activity"],
                        r["total_score"],
                        r["quadrant"],
                        r["ai_recommendation"],
                        f"{r['ai_confidence']}%",
                    ]
                    for i, r in enumerate(data["leaderboard"])
                ],
                [
                    width * 0.05,
                    width * 0.14,
                    width * 0.24,
                    width * 0.06,
                    width * 0.11,
                    width * 0.24,
                    width * 0.11,
                ],
                styles,
            )
        )
    story.append(Spacer(1, 6))
    story.append(
        Paragraph(
            "Reasoning: every recommendation is derived from the opportunity's "
            "pain area, current method, required AI intervention, impact area, "
            "time spent, priority and feasibility. See the Opportunity Register "
            "for full per-record explanations.",
            styles["body"],
        )
    )
    return story


def _pdf_department(data, styles, width):
    story = [
        Paragraph("Where is the AI opportunity concentrated?", styles["h2"]),
        _tbl(
            ["Department", "Opportunities", "Hours / Month", "Avg Score", "Quick Wins", "Top AI Solution"],
            [
                [
                    d["department"],
                    d["opportunities"],
                    d["hours"],
                    d["avg_score"],
                    d["quick_wins"],
                    d["top_solution"],
                ]
                for d in data["department_summary"]
            ],
            [
                width * 0.2,
                width * 0.14,
                width * 0.14,
                width * 0.12,
                width * 0.12,
                width * 0.28,
            ],
            styles,
        ),
    ]
    if data["leaderboard"]:
        story.append(Paragraph("Top opportunity per department", styles["h2"]))
        rows = []
        seen = set()
        for r in data["register"]:
            if r["department"] in seen:
                continue
            seen.add(r["department"])
            rows.append(
                [
                    r["department"],
                    r["process_activity"],
                    r["total_score"],
                    r["ai_recommendation"],
                    f"{r['ai_confidence']}%",
                ]
            )
        story.append(
            _tbl(
                ["Department", "Top Opportunity", "Score", "AI Recommendation", "Confidence"],
                rows,
                [
                    width * 0.2,
                    width * 0.3,
                    width * 0.08,
                    width * 0.26,
                    width * 0.16,
                ],
                styles,
            )
        )
    return story


def _pdf_executive(data, styles, width):
    story = [
        Paragraph("Headline numbers", styles["h2"]),
        _tbl(
            ["Metric", "Value"],
            [
                ["AI opportunities identified", data["report_count"]],
                ["Monthly hours consumed today", f"{data['total_hours']} hours"],
                ["Departments with opportunities", data["departments"]],
                ["Quick wins ready to start", data["quadrant_counts"]["Quick Win"]],
                ["Strategic initiatives", data["quadrant_counts"]["Strategic"]],
                ["Avg impact score (of 3)", data["avg_impact"]],
            ],
            [width * 0.6, width * 0.4],
            styles,
        ),
    ]
    if data["leaderboard"]:
        story.append(Paragraph("Top opportunities to action", styles["h2"]))
        story.append(
            _tbl(
                ["Rank", "Department", "Process / Activity", "Score", "Quadrant", "AI Recommendation", "Confidence"],
                [
                    [
                        i + 1,
                        r["department"],
                        r["process_activity"],
                        r["total_score"],
                        r["quadrant"],
                        r["ai_recommendation"],
                        f"{r['ai_confidence']}%",
                    ]
                    for i, r in enumerate(data["leaderboard"][:5])
                ],
                [
                    width * 0.05,
                    width * 0.14,
                    width * 0.24,
                    width * 0.06,
                    width * 0.11,
                    width * 0.24,
                    width * 0.11,
                ],
                styles,
            )
        )
    story.append(Paragraph("Recommended AI solutions", styles["h2"]))
    story.append(
        _tbl(
            ["AI Solution", "Opportunities", "Share"],
            [
                [name, d["count"], f"{round(d['count'] / max(1, data['report_count']) * 100)}%"]
                for name, d in [
                    (item["name"], item) for item in data["solution_distribution"]
                ]
            ],
            [width * 0.6, width * 0.2, width * 0.2],
            styles,
        )
    )
    return story


def _pdf_roadmap(data, styles, width):
    story = []
    for phase_key, phase in data["roadmap"].items():
        story.append(Paragraph(f"{phase['title']}  ·  {phase['timeframe']}", styles["h2"]))
        story.append(Paragraph(_escape(phase["focus"]), styles["body"]))
        if phase["items"]:
            story.append(
                _tbl(
                    ["Process / Activity", "Department", "Score", "Quadrant", "AI Recommendation", "Confidence"],
                    [
                        [
                            r["process_activity"],
                            r["department"],
                            r["total_score"],
                            r["quadrant"],
                            r["ai_recommendation"],
                            f"{r['ai_confidence']}%",
                        ]
                        for r in phase["items"][:12]
                    ],
                    [
                        width * 0.3,
                        width * 0.14,
                        width * 0.07,
                        width * 0.12,
                        width * 0.22,
                        width * 0.15,
                    ],
                    styles,
                )
            )
        else:
            story.append(Paragraph("No opportunities in this phase yet.", styles["body"]))
        story.append(Spacer(1, 4))
    return story


def _pdf_register(data, styles, width):
    story = []
    rows = data["register"]
    if not rows:
        story.append(Paragraph("No opportunities recorded.", styles["body"]))
        return story
    headers = ["Date", "Department", "Process / Activity", "Hours", "Score", "Quadrant", "Status", "AI Recommendation", "Confidence"]
    widths = [
        width * 0.09,
        width * 0.13,
        width * 0.24,
        width * 0.06,
        width * 0.06,
        width * 0.11,
        width * 0.1,
        width * 0.15,
        width * 0.06,
    ]
    body = []
    for r in rows:
        body.append(
            [
                r["date"],
                r["department"],
                r["process_activity"],
                _fmt_hours(r["time_spent_hrs"]),
                r["total_score"],
                r["quadrant"],
                r["status"],
                r["ai_recommendation"],
                f"{r['ai_confidence']}%",
            ]
        )
    chunk = 40
    for i in range(0, len(body), chunk):
        if i > 0:
            story.append(PageBreak())
        story.append(_tbl(headers, body[i:i + chunk], widths, styles))
    return story


def export_report(report_type, fmt, records):
    """Return (mimetype, extension, bytes) for the requested report."""
    data = build_report_data(records)
    if fmt == "xlsx":
        return (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xlsx",
            _render_xlsx(report_type, records, data),
        )
    if fmt == "csv":
        return ("text/csv", "csv", _render_csv(report_type, records, data))
    return ("application/pdf", "pdf", _render_pdf(report_type, records, data))

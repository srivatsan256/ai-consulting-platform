"""Rule-based AI assistant for the AI Intervention Pain Areas Tracker.

Maps a natural-language question to a filtered query over the
AIInterventionPainArea model. No LLM is used - this is deterministic
keyword/intent matching that only ever returns results computed from
real data.
"""
import re

from .models import AIInterventionPainArea
from .scoring import (
    score_from_priority,
    score_from_time_spent,
    quadrant_from_scores,
)


def _total_score(obj):
    impact = score_from_time_spent(obj.time_spent_hrs)
    feasibility = score_from_priority(obj.feasibility)
    priority = score_from_priority(obj.priority)
    return impact + feasibility + priority


def _quadrant(obj):
    impact = score_from_time_spent(obj.time_spent_hrs)
    feasibility = score_from_priority(obj.feasibility)
    return quadrant_from_scores(impact, feasibility)


def _record_payload(r):
    return {
        "id": r.id,
        "process_activity": r.process_activity,
        "department": r.department,
        "pain_area": r.pain_area,
        "time_spent_hrs": r.time_spent_hrs,
        "status": r.status,
        "priority": r.priority,
        "quadrant": _quadrant(r),
        "total_score": _total_score(r),
        "owner": r.owner,
        "ai_recommendation": r.ai_intervention,
    }


def _parse_n(q):
    """Extract a leading integer like 'top 5 opportunities'."""
    m = re.search(r"(?:top\s+|best\s+|first\s+)?(\d+)", q.lower())
    if m:
        return min(int(m.group(1)), 50)
    return 5


def intent_quick_wins(qn):
    return any(k in qn for k in ["quick win", "quick-wins", "quickwins"])


def intent_open(qn):
    return any(k in qn for k in ["open opportunity", "open opportunit", "status open", "open ones"])


def intent_top(qn):
    return any(k in qn for k in ["top ", "highest ", "best ", "most "]) and any(
        k in qn for k in ["opportunit", "project", "pain", "process", "score"]
    )


def intent_high_priority(qn):
    return any(k in qn for k in ["high priority", "highest priority", "priority score"])


def intent_hours_dept(qn):
    return any(k in qn for k in ["manual effort", "most hours", "highest hours", "most manual", "total hours"])


def intent_by_status(qn):
    for status_ in ["cancelled", "on hold", "in progress", "completed", "open"]:
        if status_ in qn and "status" in qn:
            return status_
    return None
def answer(question):
    """Return a structured response dict built from real query results."""
    qn = (question or "").lower().strip()
    if not qn:
        return {"status": "error", "message": "Please ask a question.", "data": None}

    status_name = intent_by_status(qn)
    if status_name:
        status_lookup = {
            "completed": "Completed",
            "in progress": "In Progress",
            "on hold": "On Hold",
            "cancelled": "Cancelled",
            "open": "Open",
        }
        objs = list(
            AIInterventionPainArea.objects.filter(status=status_lookup[status_name])
        )
        return {
            "status": "ok",
            "intent": "by_status",
            "message": (
                f"Found {len(objs)} opportunity/opportunities with status "
                f'"{status_lookup[status_name]}".'
            ),
            "data": [_record_payload(o) for o in objs],
        }

    if intent_top(qn):
        n = _parse_n(qn)
        objs = sorted(
            AIInterventionPainArea.objects.all(),
            key=lambda o: _total_score(o),
            reverse=True,
        )[:n]
        return {
            "status": "ok",
            "intent": "top",
            "message": f"Here are the top {len(objs)} opportunities by total score.",
            "data": [_record_payload(o) for o in objs],
        }

    if intent_quick_wins(qn):
        objs = [
            o for o in AIInterventionPainArea.objects.all()
            if _quadrant(o) == "Quick Win"
        ]
        return {
            "status": "ok",
            "intent": "quick_wins",
            "message": f"Found {len(objs)} Quick Win opportunities.",
            "data": [_record_payload(o) for o in objs],
        }

    if intent_high_priority(qn):
        objs = [
            o for o in AIInterventionPainArea.objects.all()
            if _total_score(o) >= 7
        ]
        return {
            "status": "ok",
            "intent": "high_priority",
            "message": f"Found {len(objs)} high-priority opportunities (total score >= 7).",
            "data": [_record_payload(o) for o in objs],
        }

    if intent_hours_dept(qn):
        dept_map = {}
        for o in AIInterventionPainArea.objects.all():
            d = o.department or "Unknown"
            dept_map[d] = dept_map.get(d, 0) + (o.time_spent_hrs or 0)
        ranked = sorted(dept_map.items(), key=lambda kv: kv[1], reverse=True)[:10]
        data = [{"department": d, "hours": round(h, 2)} for d, h in ranked]
        return {
            "status": "ok",
            "intent": "hours_department",
            "message": (
                f'Department with the highest manual effort is "{data[0]["department"]}" '
                f'at {data[0]["hours"]} hrs/month.'
                if data
                else "No department data found."
            ),
            "data": data,
        }

    # Fallback: overview stats
    total = AIInterventionPainArea.objects.count()
    hours = sum(
        (o.time_spent_hrs or 0) for o in AIInterventionPainArea.objects.all()
    )
    counts = {"Quick Win": 0, "Strategic": 0, "Fill In": 0, "Revisit": 0}
    open_count = 0
    for o in AIInterventionPainArea.objects.all():
        q = _quadrant(o)
        if q in counts:
            counts[q] += 1
        if o.status == "Open":
            open_count += 1
    return {
        "status": "ok",
        "intent": "overview",
        "message": (
            f"I couldn't map that to a specific query. Here is a portfolio "
            f"overview: {total} opportunities, {round(hours, 1)} hrs/month, "
            f'{counts["Quick Win"]} Quick Wins, {open_count} open.'
        ),
        "data": {
            "total": total,
            "hours": round(hours, 1),
            "quadrants": counts,
            "open": open_count,
        },
    }

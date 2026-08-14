"""Shared scoring helpers for the AI Intervention Pain Areas Tracker.

These mirror the GENERATED ALWAYS AS expressions stored on the Supabase
table (see sql/add_calculated_fields.sql) so the API returns identical values
regardless of the database backend.
"""


def score_from_priority(value):
    return {"High": 3, "Medium": 2, "Low": 1}.get(value, 1)


def score_from_time_spent(time_spent_hrs):
    if time_spent_hrs is None:
        return 1
    if time_spent_hrs >= 40:
        return 3
    if time_spent_hrs >= 10:
        return 2
    return 1


def quadrant_from_scores(impact_score, feasibility_score):
    if impact_score >= 2 and feasibility_score >= 2:
        return "Quick Win"
    if impact_score >= 2:
        return "Strategic"
    if feasibility_score >= 2:
        return "Fill In"
    return "Revisit"

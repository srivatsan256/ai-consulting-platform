"""Shared scoring helpers for the AI Intervention Pain Areas Tracker.

These mirror the GENERATED ALWAYS AS expressions stored on the Supabase
table (see sql/add_calculated_fields.sql) so the API returns identical values
regardless of the database backend.

Scoring Scale (1–3):
--------------------
Impact Score  — derived from Time Spent / Month (hrs):
  None / missing → None  ("Needs Input")
  < 10 hrs       → 1  (low)
  10–39 hrs      → 2  (medium)
  ≥ 40 hrs       → 3  (high)

Feasibility Score — derived from Feasibility field (High / Medium / Low):
  High   → 3
  Medium → 2
  Low    → 1

Priority Score — derived from Priority field (High / Medium / Low):
  High   → 3
  Medium → 2
  Low    → 1

Quadrant Assignment (Impact × Feasibility thresholds):
  Quick Win     : Impact ≥ 2, Feasibility ≥ 2  → do first
  Strategic     : Impact ≥ 2, Feasibility < 2   → plan & resource
  Fill In       : Impact < 2, Feasibility ≥ 2   → nice to have
  Revisit       : Impact < 2, Feasibility < 2   → deprioritize
  Needs Input   : any score is None             → data gap
"""

LEVEL_TO_SCORE = {"High": 3, "Medium": 2, "Low": 1}


def score_from_priority(value):
    """Return a 1–3 score from a High/Medium/Low priority string.
    Returns None when value is absent or unrecognised."""
    if not value:
        return None
    return LEVEL_TO_SCORE.get(value, None)


def score_from_feasibility(value):
    """Return a 1–3 score from a High/Medium/Low feasibility string.
    Returns None when value is absent or unrecognised."""
    if not value:
        return None
    return LEVEL_TO_SCORE.get(value, None)


def score_from_time_spent(time_spent_hrs):
    """Return a 1–3 impact score derived from monthly time spent (hours).

    Bands
    -----
    None / missing → None  ("Needs Input")
    < 10 hrs       → 1
    10–39 hrs      → 2
    ≥ 40 hrs       → 3
    """
    if time_spent_hrs is None:
        return None
    if time_spent_hrs >= 40:
        return 3
    if time_spent_hrs >= 10:
        return 2
    return 1


def needs_input(obj):
    """Return True when the record is missing data required to compute scores.

    Currently the only field that can be genuinely absent is time_spent_hrs
    (the priority and feasibility fields always have a model default).
    """
    return obj.time_spent_hrs is None


def quadrant_from_scores(impact_score, feasibility_score):
    """Assign a prioritisation quadrant based on 1–3 Impact and Feasibility scores.

    Thresholds
    ----------
    Quick Win     : Impact ≥ 2, Feasibility ≥ 2
    Strategic     : Impact ≥ 2, Feasibility < 2
    Fill In       : Impact < 2, Feasibility ≥ 2
    Revisit       : Impact < 2, Feasibility < 2
    Needs Input   : either score is None
    """
    if impact_score is None or feasibility_score is None:
        return "Needs Input"
    high_impact = impact_score >= 2
    high_feasibility = feasibility_score >= 2
    if high_impact and high_feasibility:
        return "Quick Win"
    if high_impact and not high_feasibility:
        return "Strategic"
    if not high_impact and high_feasibility:
        return "Fill In"
    return "Revisit"

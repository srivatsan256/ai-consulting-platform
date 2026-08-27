"""AI recommendation engine (Modules 4.1 - 4.3).

Given a pain-area record's fields (pain area, current method, AI intervention
required, impact area, time spent, priority, feasibility) the engine suggests
one of the eight AI solution types, a confidence percentage and a natural
language reasoning.

The engine is fully deterministic and keyword driven - no external LLM call is
required, so it runs instantly on every record and every export.
"""

import re

from .scoring import (
    score_from_priority,
    score_from_feasibility,
    score_from_time_spent,
    quadrant_from_scores,
)

# The eight AI solution types the platform can recommend.
AI_SOLUTIONS = [
    {
        "key": "generative_ai_assistant",
        "name": "Generative AI Assistant",
        "icon": "auto_awesome",
        "description": (
            "An assistant that drafts, summarises and rewrites text, emails, "
            "reports and documents using a large language model."
        ),
        "benefit": (
            "Reduces manual writing effort, speeds up content production and "
            "keeps output consistent and on-brand."
        ),
        "keywords": [
            "report",
            "write",
            "writing",
            "written",
            "draft",
            "drafting",
            "email",
            "summar",
            "summary",
            "content",
            "create",
            "creating",
            "letter",
            "memo",
            "meeting minutes",
            "translate",
            "rewrite",
            "format",
            "generate",
        ],
    },
    {
        "key": "ai_knowledge_base",
        "name": "AI Knowledge Base",
        "icon": "database",
        "description": (
            "A searchable repository of policies, procedures and answers "
            "powered by AI that employees can query in natural language."
        ),
        "benefit": (
            "Puts answers at employees' fingertips, cuts onboarding time and "
            "reduces repeated questions to central teams."
        ),
        "keywords": [
            "knowledge",
            "faq",
            "question",
            "answer",
            "onboarding",
            "information",
            "policy",
            "guideline",
            "procedure",
            "how-to",
            "how to",
            "self-service",
            "self service",
            "training",
            "reference",
            "manual",
            "learn",
        ],
    },
    {
        "key": "workflow_automation",
        "name": "Workflow Automation",
        "icon": "sync_alt",
        "description": (
            "Software bots and workflow engines that perform routine, "
            "rule-based steps without human intervention."
        ),
        "benefit": (
            "Eliminates repetitive manual work, removes transcription errors "
            "and frees staff for higher-value tasks."
        ),
        "keywords": [
            "data entry",
            "manual",
            "repetitive",
            "routine",
            "copy",
            "paste",
            "route",
            "routing",
            "approval",
            "approve",
            "process",
            "processing",
            "transfer",
            "move",
            "upload",
            "download",
            "update",
            "reconcil",
            "spreadsheet",
            "excel",
            "input",
            "tracking",
        ],
    },
    {
        "key": "predictive_analytics",
        "name": "Predictive Analytics",
        "icon": "trending_up",
        "description": (
            "Machine learning models that forecast future outcomes such as "
            "demand, churn, risk and resource needs."
        ),
        "benefit": (
            "Turns historical data into forward-looking insight so teams can "
            "act before problems or opportunities appear."
        ),
        "keywords": [
            "forecast",
            "predict",
            "prediction",
            "trend",
            "demand",
            "churn",
            "sales",
            "budget",
            "projection",
            "risk",
            "likelihood",
            "anticipate",
            "planning",
            "seasonal",
            "usage",
            "growth",
            "forecasting",
        ],
    },
    {
        "key": "intelligent_search",
        "name": "Intelligent Search",
        "icon": "search",
        "description": (
            "Enterprise search that finds information, files and records "
            "across systems using semantic matching and filters."
        ),
        "benefit": (
            "Dramatically shortens the time people spend hunting for "
            "information scattered across the organisation."
        ),
        "keywords": [
            "search",
            "find",
            "locate",
            "retrieve",
            "lookup",
            "look up",
            "file",
            "archive",
            "database",
            "query",
            "navigate",
            "filter",
        ],
    },
    {
        "key": "document_intelligence",
        "name": "Document Intelligence",
        "icon": "description",
        "description": (
            "AI that reads, classifies and extracts data from invoices, "
            "contracts, forms and PDFs automatically."
        ),
        "benefit": (
            "Automates document-heavy workflows, improves accuracy and keeps "
            "compliance reviews consistent and auditable."
        ),
        "keywords": [
            "invoice",
            "contract",
            "form",
            "extract",
            "extraction",
            "pdf",
            "scan",
            "scanned",
            "parse",
            "compliance",
            "review",
            "validate",
            "verify",
            "ocr",
            "policy",
            "document",
            "documents",
        ],
    },
    {
        "key": "ai_decision_support",
        "name": "AI Decision Support",
        "icon": "psychology",
        "description": (
            "Models that weigh options, score alternatives and recommend "
            "decisions backed by explainable criteria."
        ),
        "benefit": (
            "Helps teams evaluate trade-offs consistently and make better, "
            "data-driven decisions faster."
        ),
        "keywords": [
            "decision",
            "decide",
            "choose",
            "selection",
            "select",
            "evaluate",
            "evaluation",
            "assess",
            "assessment",
            "option",
            "trade-off",
            "tradeoff",
            "prioritise",
            "prioritize",
            "recommendation",
            "scoring",
            "compare",
        ],
    },
    {
        "key": "conversational_ai",
        "name": "Conversational AI",
        "icon": "forum",
        "description": (
            "Chatbots and virtual assistants that answer customers and "
            "employees, resolve tickets and route requests."
        ),
        "benefit": (
            "Answers routine queries instantly around the clock, cuts queue "
            "times and reduces load on support teams."
        ),
        "keywords": [
            "support",
            "customer",
            "help desk",
            "helpdesk",
            "call center",
            "chat",
            "query",
            "respond",
            "ticket",
            "service",
            "complaint",
            "inquiry",
            "enquiry",
            "request",
            "assistance",
        ],
    },
]

SOLUTION_BY_NAME = {s["name"]: s for s in AI_SOLUTIONS}

# Weights per field so that pain point and required-intervention text weigh
# more than the shorter label fields.
_FIELD_WEIGHTS = {
    "pain_area": 3,
    "current_method": 2,
    "ai_intervention": 3,
    "impact_area": 1,
    "process_activity": 2,
}
_TOTAL_WEIGHT = sum(_FIELD_WEIGHTS.values())

# Phrases used to describe how much manual time the process consumes.
_TIME_PHRASES = {
    3: "a very large amount of time (40+ hours per month)",
    2: "a significant amount of time (10-40 hours per month)",
    1: "some staff time each month",
}

_PRIORITY_TEXT = {"High": "high", "Medium": "medium", "Low": "lower"}
_FEASIBILITY_TEXT = {"High": "highly feasible", "Medium": "reasonably feasible", "Low": "less feasible"}

# Closing sentence per solution describing the practical outcome.
_OUTCOME_HINTS = {
    "generative_ai_assistant": (
        "A generative AI assistant integrated with your templates could draft "
        "this work automatically and keep the output consistent."
    ),
    "ai_knowledge_base": (
        "An AI knowledge base could capture this know-how once and answer "
        "these questions for everyone instantly."
    ),
    "workflow_automation": (
        "Workflow automation could run these steps automatically and remove "
        "the manual effort entirely."
    ),
    "predictive_analytics": (
        "Predictive analytics could forecast this pattern and let you plan "
        "earlier with confidence."
    ),
    "intelligent_search": (
        "Intelligent search could return the right information in seconds "
        "instead of minutes."
    ),
    "document_intelligence": (
        "Document intelligence could read and extract this information "
        "automatically, with a clear audit trail."
    ),
    "ai_decision_support": (
        "AI decision support could score the alternatives and recommend the "
        "best option with explainable reasoning."
    ),
    "conversational_ai": (
        "A conversational AI assistant could answer these requests instantly, "
        "around the clock, without human involvement."
    ),
}

_WORD_BOUNDARY = re.compile(r"(?<![a-z])")


def _tokenize(value):
    return str(value or "").lower()


def _matches(text, keyword):
    if not text:
        return False
    if " " in keyword:
        return keyword in text
    return bool(re.search(r"\b" + re.escape(keyword) + r"(?:s|ing|ed|e)?\b", text))


def _keyword_hits(text, solution):
    hits = []
    for kw in solution["keywords"]:
        if _matches(text, kw):
            hits.append(kw)
    return hits


def _score_solution(record, solution):
    """Return (weighted_score, matched_keywords) for one solution."""
    score = 0
    all_hits = []
    for field, weight in _FIELD_WEIGHTS.items():
        text = _tokenize(record.get(field))
        if not text:
            continue
        for kw in solution["keywords"]:
            if _matches(text, kw):
                score += weight
                all_hits.append(kw)
    return score, sorted(set(all_hits))


def recommend(record):
    """Return a dict with the recommended AI solution, confidence and reasoning.

    ``record`` may be a model instance or a plain dict.
    """
    if not hasattr(record, "get"):
        record = {
            "pain_area": record.pain_area,
            "current_method": record.current_method,
            "ai_intervention": record.ai_intervention,
            "impact_area": record.impact_area,
            "process_activity": record.process_activity,
            "frequency": record.frequency,
            "time_spent_hrs": record.time_spent_hrs,
            "priority": record.priority,
            "feasibility": record.feasibility,
            "remarks": record.remarks,
        }

    time_spent = None
    if record.get("time_spent_hrs") is not None:
        try:
            time_spent = float(record.get("time_spent_hrs"))
        except (TypeError, ValueError):
            time_spent = None

    time_score = score_from_time_spent(time_spent)
    priority = record.get("priority") or "Medium"
    feasibility = record.get("feasibility") or "Medium"
    priority_score = score_from_priority(priority)
    feasibility_score = score_from_feasibility(feasibility)

    ranked = [
        (_score_solution(record, sol), sol)
        for sol in AI_SOLUTIONS
    ]
    ranked.sort(key=lambda item: -item[0][0])

    (top_score, top_hits), top_solution = ranked[0]
    (second_score, _), _ = ranked[1]

    # Fallback for records with no keyword signals: infer from structure.
    if top_score == 0:
        if time_spent is not None and time_spent >= 10:
            top_solution = SOLUTION_BY_NAME["Workflow Automation"]
            top_hits = ["high manual time"]
        else:
            top_solution = SOLUTION_BY_NAME["Generative AI Assistant"]
            top_hits = ["process improvement opportunity"]

    # ----- Confidence -----
    # Keyword evidence drives the base; structural signals add on top.
    match_ratio = min(1.0, top_score / _TOTAL_WEIGHT)
    confidence = 48 + round(match_ratio * 32)
    if top_score > 0 and second_score > 0:
        confidence += 3  # strong signal over the runner-up

    if time_score is not None and time_score >= 3:
        confidence += 10
    elif time_score is not None and time_score == 2:
        confidence += 5
    if priority_score >= 3:
        confidence += 5
    elif priority_score == 2:
        confidence += 2
    if feasibility_score >= 3:
        confidence += 5
    elif feasibility_score == 2:
        confidence += 2

    ai_req = _tokenize(record.get("ai_intervention"))
    if ai_req and top_solution["name"].lower() in ai_req:
        confidence += 8

    confidence = max(55, min(98, confidence))

    # ----- Reasoning -----
    reasons = []
    if time_spent is not None:
        reasons.append(
            f"This process is repeated {_TIME_PHRASES[time_score]}, "
            f"consuming about {time_spent:g} hours per month."
        )
    elif record.get("frequency"):
        reasons.append(
            f"This process is repeated {str(record.get('frequency')).lower()}."
        )
    else:
        reasons.append("This process involves recurring manual effort.")

    quadrant = quadrant_from_scores(time_score, feasibility_score)
    reasons.append(
        f"It has {_PRIORITY_TEXT.get(priority, 'medium')} priority and is "
        f"{_FEASIBILITY_TEXT.get(feasibility, 'reasonably feasible')} "
        f"(impact {time_score}/3, feasibility {feasibility_score}/3, "
        f"{quadrant})."
    )

    if top_hits:
        evidence = ", ".join(f'"{h}"' for h in top_hits[:5])
        reasons.append(
            f"The pain point centres on {evidence}, which is a classic fit "
            f"for {top_solution['name']}."
        )

    reasons.append(_OUTCOME_HINTS[top_solution["key"]])

    return {
        "key": top_solution["key"],
        "name": top_solution["name"],
        "icon": top_solution["icon"],
        "description": top_solution["description"],
        "benefit": top_solution["benefit"],
        "confidence": confidence,
        "reasoning": " ".join(reasons),
        "reasons": reasons,
    }


def solution_distribution(records):
    """Count how many records map to each of the eight AI solutions."""
    counts = {s["name"]: 0 for s in AI_SOLUTIONS}
    for rec in records:
        name = recommend(rec)["name"]
        counts[name] = counts.get(name, 0) + 1
    return counts

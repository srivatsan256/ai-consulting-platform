"""
verification/keyword_matcher.py
Keyword and section presence checker for different document types.
"""
import re
from typing import Dict, List

# -----------------------------------------------------------------------
# Document-type keyword definitions
# Extend these lists freely to match your consulting requirements.
# -----------------------------------------------------------------------

KEYWORDS: Dict[str, List[str]] = {
    "BRD": [
        "business requirements",
        "stakeholders",
        "scope",
        "objectives",
        "assumptions",
        "constraints",
        "acceptance criteria",
        "business rules",
    ],
    "FRD": [
        "functional requirements",
        "use cases",
        "user stories",
        "system behavior",
        "data flow",
        "interfaces",
        "input",
        "output",
    ],
    "PRD": [
        "product requirements",
        "features",
        "user personas",
        "roadmap",
        "success metrics",
        "priority",
        "release",
    ],
    "SOP": [
        "standard operating procedure",
        "process flow",
        "responsibilities",
        "steps",
        "compliance",
        "review",
    ],
    "OTHER": [],
}

SECTIONS: Dict[str, List[str]] = {
    "BRD": [
        "executive summary",
        "project overview",
        "stakeholder analysis",
        "requirements",
        "out of scope",
        "glossary",
    ],
    "FRD": [
        "introduction",
        "system overview",
        "functional requirements",
        "non-functional requirements",
        "appendix",
    ],
    "PRD": [
        "introduction",
        "problem statement",
        "goals",
        "requirements",
        "timeline",
    ],
    "SOP": [
        "purpose",
        "scope",
        "procedure",
        "references",
    ],
    "OTHER": [],
}


def find_missing_keywords(text: str, doc_type: str) -> List[str]:
    """Return keywords that are absent (case-insensitive) from the text."""
    required = KEYWORDS.get(doc_type, KEYWORDS["OTHER"])
    return [kw for kw in required if not re.search(re.escape(kw), text, re.IGNORECASE)]


def find_missing_sections(text: str, doc_type: str) -> List[str]:
    """Return section headers that are absent (case-insensitive) from the text."""
    required = SECTIONS.get(doc_type, SECTIONS["OTHER"])
    return [sec for sec in required if not re.search(re.escape(sec), text, re.IGNORECASE)]

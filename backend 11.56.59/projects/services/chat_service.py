"""
Rule-based document assistant.

Answers questions about a project by searching the extracted text of its
uploaded documents. No external LLM dependency is required, which keeps the
integration working offline while remaining easy to swap for a real model.
"""

from __future__ import annotations

import re

STOPWORDS = {
    "what", "whats", "are", "the", "is", "for", "and", "with", "that",
    "this", "from", "how", "can", "you", "tell", "about", "summarize",
    "summarise", "give", "list", "please", "would", "could", "project",
    "document", "documents", "does", "did", "when", "who", "where", "why",
    "have", "has", "which", "them", "their", "there",
}


def _tokenize(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _extract_excerpt(text: str, keywords: list, window: int = 300) -> str | None:
    lower = text.lower()
    best = None
    for kw in keywords:
        idx = lower.find(kw)
        if idx == -1:
            continue
        start = max(0, idx - window // 2)
        end = min(len(text), idx + len(kw) + window // 2)
        candidate = text[start:end].replace("\n", " ").strip()
        if best is None or len(candidate) > len(best):
            best = candidate
        break
    if best is None and text.strip():
        return text[:window].replace("\n", " ").strip()
    return best


def answer_question(project, question: str) -> str:
    question_lower = (question or "").strip().lower()

    if not question_lower:
        return "Please ask a question about this project's documents."

    # Direct answers from project metadata
    if "timeline" in question_lower or "schedule" in question_lower or "duration" in question_lower:
        if project.expected_timeline:
            return (
                f"The expected timeline for {project.project_name} is "
                f"{project.expected_timeline}."
            )
    if "objective" in question_lower or "goal" in question_lower or "business" in question_lower:
        if project.objectives:
            return (
                f"The objectives of {project.project_name} are: "
                f"{project.objectives}"
            )
    if "risk" in question_lower:
        hits = _search_documents(project, ["risk", "mitigation", "hazard"])
        if hits:
            return hits[0][1]
    if "stakeholder" in question_lower or "participant" in question_lower:
        hits = _search_documents(project, ["stakeholder", "participant", "audience"])
        if hits:
            return hits[0][1]

    hits = _search_documents(project, _tokenize(question_lower) - STOPWORDS)

    if not hits:
        return (
            f"I could not find information about that in the documents "
            f"uploaded for {project.project_name}. Try asking about the "
            "objectives, timeline, risks, or stakeholders."
        )

    # Deduplicate excerpts
    seen = set()
    parts = []
    for _, excerpt in hits:
        key = excerpt[:80]
        if key in seen:
            continue
        seen.add(key)
        parts.append(excerpt)
        if len(parts) >= 3:
            break

    return "Based on the uploaded documents:\n\n" + "\n\n".join(f"- {p}" for p in parts)


def _search_documents(project, keywords: list) -> list:
    keyword_list = [kw for kw in keywords if len(kw) >= 3]

    if not keyword_list:
        return []

    results = []
    for doc in project.uploaded_documents.all():
        text = doc.extracted_text or ""
        if not text:
            continue
        lower = text.lower()
        score = sum(1 for kw in keyword_list if kw in lower)
        if score == 0:
            continue
        excerpt = _extract_excerpt(text, keyword_list)
        if excerpt:
            results.append((score, excerpt))

    results.sort(key=lambda item: item[0], reverse=True)
    return results

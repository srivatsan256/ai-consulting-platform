"""
Level-based document verification.

Documents uploaded for a level are matched against the requirements defined
in the matching ``LevelModule``. Each document produces a score and the level
passes when every uploaded document satisfies all of its required items.
"""

from __future__ import annotations

from core.document_processor import extract_text_from_uploaded_file
from projects.models import LevelModule, ProjectDocument


def _requirement_text(item) -> str:
    if isinstance(item, dict):
        return str(item.get("text", "")).strip()
    return str(item).strip()


def verify_document(doc: ProjectDocument, level_module: LevelModule | None = None) -> dict:
    """Verify a single uploaded document against level requirements."""
    if level_module is None:
        level_module = LevelModule.objects.filter(level=doc.level).first()

    must_include = list(level_module.must_include or []) if level_module else []
    requirements = [_requirement_text(item) for item in must_include]
    requirements = [r for r in requirements if r]

    text = (doc.extracted_text or "").lower()

    missing = [req for req in requirements if req.lower() not in text]
    present = len(requirements) - len(missing)

    total = len(requirements)

    if total == 0:
        score = 100
        passed = True
    else:
        score = round((present / total) * 100)
        passed = missing == []

    doc.verification_status = passed
    doc.verification_score = score
    doc.missing_requirements = missing
    doc.save(update_fields=[
        "verification_status",
        "verification_score",
        "missing_requirements",
    ])

    feedback = _build_feedback(doc.doc_type, score, missing)

    return {
        "document_id": doc.id,
        "doc_type": doc.doc_type,
        "level": doc.level,
        "score": score,
        "passed": passed,
        "page_number": None,
        "match_method": "keyword",
        "confidence": round(present / total, 2) if total else 1.0,
        "ocr_used": False,
        "evidence": (
            f"Matched {present} of {total} required items for this level."
            if total
            else "No requirements are configured for this level."
        ),
        "coordinates": None,
        "missing_keywords": missing,
        "missing_sections": [],
        "ai_feedback": feedback,
    }


def _build_feedback(doc_type: str, score: int, missing: list) -> str:
    if not missing:
        return (
            f"The {doc_type} document is complete for the current level. "
            "All required items were found."
        )
    summary = ", ".join(missing[:3])
    more = f" and {len(missing) - 3} more" if len(missing) > 3 else ""
    return (
        f"The {doc_type} document scores {score}%. The following required "
        f"items could not be found: {summary}{more}. Please revise and "
        "re-upload the document."
    )


def verify_project(project, use_ai: bool = False) -> dict:
    """Run verification across all documents at the project's current level."""
    level = max(1, project.current_level or 1)

    level_module = LevelModule.objects.filter(level=level).first()

    docs = list(project.uploaded_documents.filter(level=level))

    results = [verify_document(doc, level_module) for doc in docs]

    if results:
        readiness = round(
            sum(r["score"] for r in results) / len(results)
        )
    else:
        readiness = 0

    level_passed = bool(results) and all(r["passed"] for r in results)

    report = {
        "level": level,
        "level_status": "PASSED" if level_passed else "FAILED",
        "unlock_next_level": level_passed,
        "readiness_score": readiness,
        "status": "PASSED" if level_passed else "FAILED",
        "results": results,
    }

    project.readiness_score = readiness

    level_scores = dict(project.level_scores or {})
    level_scores[str(level)] = readiness

    if level_passed:
        completed = list(project.completed_levels or [])
        if level not in completed:
            completed.append(level)
        project.completed_levels = completed
        project.current_level = level + 1

    project.level_scores = level_scores
    project.verification_report = report
    project.save(update_fields=[
        "readiness_score",
        "level_scores",
        "completed_levels",
        "current_level",
        "verification_report",
        "updated_at",
    ])

    return report


def extract_text(doc: ProjectDocument) -> str:
    """Extract and persist the text of an uploaded document."""
    try:
        result = extract_text_from_uploaded_file(doc.file)
        text = result.get("text", "") or ""
    except Exception:
        text = ""
    doc.extracted_text = text
    doc.save(update_fields=["extracted_text"])
    return text

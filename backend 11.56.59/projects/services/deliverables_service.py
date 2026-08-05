"""
Deliverable generation.

Packages BRD, FRD, PRD, verification summary, timeline and metadata into a
ZIP file stored under MEDIA_ROOT so the frontend can download it directly.
"""

from __future__ import annotations

import io
import json
import os
import zipfile

from django.conf import settings
from django.utils import timezone


def _build_brd(project) -> str:
    docs = "\n".join(
        f"- {doc.original_name} ({doc.doc_type}, score {doc.verification_score}%)"
        for doc in project.uploaded_documents.all()
    ) or "- No documents uploaded yet."

    return f"""# Business Requirements Document
## {project.project_name}

**Company:** {project.company.company_name}
**Industry:** {project.industry or "Not specified"}
**Timeline:** {project.expected_timeline or "Not specified"}
**Current Level:** {project.current_level}

## Objectives
{project.objectives or "Not specified"}

## Source Documents
{docs}

## Readiness
{project.readiness_score}% (Level {project.current_level - 1} completed)
"""


def _build_frd(project) -> str:
    return f"""# Functional Requirements Document
## {project.project_name}

**Company:** {project.company.company_name}
**Current Level:** {project.current_level}
**Readiness:** {project.readiness_score}%

## Functional Scope
Functional requirements are derived from the uploaded level documents and
the business objectives described below.

## Business Objectives
{project.objectives or "Not specified"}

## Team
{project.team_members or "Not specified"}
"""


def _build_prd(project) -> str:
    return f"""# Product Requirements Document
## {project.project_name}

**Company:** {project.company.company_name}

## Product Overview
{project.description or "Not specified"}

## Goals
{project.objectives or "Not specified"}

## Constraints
- Expected timeline: {project.expected_timeline or "Not specified"}
- Current maturity level: {project.current_level}
"""


def _build_verification_summary(project) -> str:
    report = project.verification_report or {}
    results = report.get("results") or []

    lines = []
    for item in results:
        status = "PASSED" if item.get("passed") else "FAILED"
        lines.append(
            f"- {item.get('doc_type')}: {status} ({item.get('score')}%)\n"
            f"  Missing: {', '.join(item.get('missing_keywords') or []) or 'None'}"
        )

    body = "\n".join(lines) or "- No verification has been run yet."

    return f"""# Verification Summary
## {project.project_name}

**Readiness Score:** {project.readiness_score}%
**Current Level:** {project.current_level}
**Generated:** {timezone.now().isoformat()}

## Results
{body}
"""


def _build_timeline(project) -> str:
    milestones = "\n".join(
        f"- {m.title} (due {m.due_date})"
        for m in project.milestones.all()
    ) or "- No milestones defined."

    return f"""# Project Timeline
## {project.project_name}

**Expected Duration:** {project.expected_timeline or "Not specified"}
**Start Date:** {project.start_date}

## Milestones
{milestones}
"""


def _build_metadata(project) -> str:
    return json.dumps(
        {
            "id": project.id,
            "name": project.project_name,
            "company": project.company.company_name,
            "industry": project.industry,
            "status": project.status,
            "priority": project.priority,
            "current_level": project.current_level,
            "completed_levels": project.completed_levels,
            "readiness_score": project.readiness_score,
            "expected_timeline": project.expected_timeline,
            "objectives": project.objectives,
            "team_members": project.team_members,
            "created_at": project.created_at.isoformat(),
        },
        indent=2,
        default=str,
    )


def generate_deliverables(project, request=None) -> str:
    """Generate the deliverable ZIP and return its absolute download URL."""
    files = {
        "BRD.md": _build_brd(project),
        "FRD.md": _build_frd(project),
        "PRD.md": _build_prd(project),
        "verification_summary.md": _build_verification_summary(project),
        "project_timeline.md": _build_timeline(project),
        "project_metadata.json": _build_metadata(project),
    }

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)

    filename = (
        f"{project.project_name.replace(' ', '_')}_deliverables_"
        f"{timezone.now().strftime('%Y%m%d_%H%M%S')}.zip"
    )

    deliverables_dir = os.path.join(settings.MEDIA_ROOT, "deliverables")
    os.makedirs(deliverables_dir, exist_ok=True)

    file_path = os.path.join(deliverables_dir, filename)
    with open(file_path, "wb") as output:
        output.write(buffer.getvalue())

    relative_url = f"{settings.MEDIA_URL}deliverables/{filename}"

    if request:
        return request.build_absolute_uri(relative_url)

    return relative_url

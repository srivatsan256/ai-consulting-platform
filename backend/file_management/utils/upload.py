"""
Shared upload pipeline for the File Management module.

Every managed project document is stored through ``create_project_document``
so the storage quota, virus-scan hook and default permissions are always
applied, no matter which endpoint triggered the upload.
"""

from __future__ import annotations

from rest_framework.exceptions import ValidationError

from projects.models import ProjectDocument

from ..models import FileCategory, FilePermission
from ..services.scanner import run_virus_scan
from ..services.storage import enforce_storage_quota


def create_project_document(
    *,
    project,
    file_obj,
    original_name: str = "",
    doc_type: str = "OTHER",
    level: int = 1,
    category_id=None,
    user,
) -> ProjectDocument:
    """
    Persist ``file_obj`` as a ``ProjectDocument`` after enforcing the
    tenant's storage quota, then run the virus-scan hook and create a
    default ``manage`` permission for the uploader.
    """
    enforce_storage_quota(project.company, file_obj.size or 0)

    category = None
    if category_id:
        category = FileCategory.objects.filter(
            company=project.company,
            pk=category_id,
        ).first()
        if category is None:
            raise ValidationError(
                {"file_category": "Invalid file category."}
            )

    try:
        parsed_level = int(level)
    except (TypeError, ValueError):
        parsed_level = None
    if not parsed_level or parsed_level < 1:
        parsed_level = project.current_level or 1

    document = ProjectDocument.objects.create(
        project=project,
        file=file_obj,
        original_name=original_name or getattr(file_obj, "name", ""),
        file_size=file_obj.size or 0,
        doc_type=str(doc_type or "OTHER").upper(),
        level=parsed_level,
        file_category=category,
        uploaded_by=user,
    )

    run_virus_scan(document)

    FilePermission.objects.get_or_create(
        file=document,
        user=user,
        role_key="",
        permission="manage",
        defaults={"allow": True, "granted_by": user},
    )

    return document

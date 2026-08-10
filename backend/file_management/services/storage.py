"""
Storage quota helpers for the File Management module.

Usage is computed from every managed file belonging to the tenant company
(project documents and task attachments). Uploads are rejected with a
``ValidationError`` when the tenant's ``StorageQuota`` would be exceeded.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.exceptions import ValidationError

from file_management.models import StorageQuota

if TYPE_CHECKING:
    from companies.models import Company


def format_bytes(size) -> str:
    """Human readable byte size, e.g. ``4.5 GB``."""
    size = float(size or 0)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} TB"


def get_storage_quota(company: "Company") -> StorageQuota:
    """Return (creating if needed) the tenant's storage quota record."""
    return StorageQuota.get_for_company(company)


def get_usage_summary(company: "Company") -> dict:
    """Summary dict of the tenant's storage usage for API responses."""
    quota = get_storage_quota(company)
    return {
        "quota_limit_bytes": quota.quota_limit_bytes,
        "used_bytes": quota.used_bytes,
        "remaining_bytes": quota.remaining_bytes,
        "usage_percent": quota.usage_percent,
        "enforced": quota.enforced,
        "over_limit": quota.remaining_bytes == 0 and quota.used_bytes > 0,
    }


def enforce_storage_quota(company: "Company", extra_bytes: int = 0) -> None:
    """
    Raise ``ValidationError`` when storing ``extra_bytes`` would push the
    tenant past its configured storage allowance.
    """
    quota = get_storage_quota(company)
    if not quota.enforced or quota.quota_limit_bytes <= 0:
        return
    projected = quota.used_bytes + int(extra_bytes or 0)
    if projected > quota.quota_limit_bytes:
        raise ValidationError(
            "Storage quota exceeded. The upload would require "
            f"{format_bytes(projected)} but the limit is "
            f"{format_bytes(quota.quota_limit_bytes)}."
        )

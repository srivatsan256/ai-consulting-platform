"""
File permission evaluation.

``check_file_access`` combines explicit ``FilePermission`` rules with
role-based defaults so project files stay tenant-safe by construction.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .models import FilePermission

if TYPE_CHECKING:
    from accounts.models import User
    from projects.models import ProjectDocument

#: Roles that always have full access to every file in their company.
ADMIN_ROLE_KEYS = {
    "super_admin",
    "company_admin",
    "project_manager",
}


def _role_keys_for_user(user: "User") -> list:
    keys = []
    assignments = getattr(user, "role_assignments", None)
    if assignments is not None:
        keys = [a.role.role_key for a in assignments.all() if a.role]
    return keys


def check_file_access(
    user: "User",
    document: "ProjectDocument",
    permission: str = "view",
) -> bool:
    """
    Return ``True`` when ``user`` may exercise ``permission`` on ``document``.

    Order of evaluation (first match wins):
      1. Company admins / project managers / uploader always have access.
      2. Explicit rules on the file: user rules, then role rules, then
         catch-all rules. An explicit ``deny`` overrides ``allow``.
      3. Everyone with a company membership may view/download by default.
    """
    if not user or not getattr(user, "is_authenticated", False):
        return False

    # Owners always pass.
    if document.uploaded_by_id == user.pk:
        return True
    role_keys = set(_role_keys_for_user(user))
    if role_keys & ADMIN_ROLE_KEYS:
        return True

    rules = FilePermission.objects.filter(file=document, permission=permission)

    # Most specific first: user -> role -> everyone.
    user_rules = rules.filter(user=user)
    if user_rules.exists():
        return user_rules.order_by("-allow").first().allow

    if role_keys:
        role_rules = rules.filter(user__isnull=True, role_key__in=role_keys)
        if role_rules.exists():
            return role_rules.order_by("-allow").first().allow

    everyone = rules.filter(user__isnull=True, role_key="")
    if everyone.exists():
        return everyone.order_by("-allow").first().allow

    # Default: any member of the owning company may view/download.
    if permission in ("view", "download"):
        return user.company_memberships.filter(
            company=document.project.company,
            is_active=True,
        ).exists()
    return False

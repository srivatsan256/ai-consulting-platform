from rest_framework.permissions import BasePermission

from core.rbac.permissions import has_feature_permission


class CanViewLoginHistory(BasePermission):
    """
    Permission to view login history.

    Users must have the appropriate permission assigned through
    the project's RBAC system or via Django permissions.
    """

    message = "You do not have permission to view login history."

    def has_permission(self, request, view) -> bool:
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Superusers always have access.
        if user.is_superuser:
            return True

        # Check RBAC system via tenant role.
        tenant = getattr(request, "tenant", None)
        role = getattr(tenant, "role", None)
        if role is not None and has_feature_permission(role, "login_history", "view"):
            return True

        # Fallback: check Django permissions.
        return user.has_perm("authentication.view_loginhistory")
from rest_framework.permissions import BasePermission


class CanViewLoginHistory(BasePermission):
    """
    Permission to view login history.

    Users must have the appropriate permission assigned through
    the project's RBAC system.
    """

    message = "You do not have permission to view login history."

    def has_permission(self, request, view) -> bool:
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Superusers always have access.
        if user.is_superuser:
            return True

        # Use Django permissions / custom RBAC.
        return user.has_perm("authentication.view_loginhistory")
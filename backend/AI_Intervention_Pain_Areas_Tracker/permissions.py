from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth.models import AbstractBaseUser


class IsAdminOrReadOnly(BasePermission):
    """
    Allow read-only access to any authenticated user.
    Write access only for staff / admin users.
    """

    def has_permission(self, request, view) -> bool:
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        # Type-safe check for is_staff
        return bool(getattr(user, "is_staff", False))
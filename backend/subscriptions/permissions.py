from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPlatformAdminOrReadOnly(BasePermission):
    """
    Allows read-only access for authenticated users, but write access only to platform superadmins.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return getattr(request.user, 'is_staff', False) or getattr(request.user, 'is_superuser', False)


class IsTenantMemberOrAdmin(BasePermission):
    """
    Ensures users can only access their own company subscription.
    Uses request.tenant for company resolution.
    """
    def has_object_permission(self, request, view, obj):
        if getattr(request.user, 'is_superuser', False):
            return True
        tenant = getattr(request, 'tenant', None)
        if not tenant or not tenant.company:
            return False
        return obj.company == tenant.company

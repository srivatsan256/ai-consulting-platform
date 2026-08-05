from rest_framework.permissions import BasePermission


class IsCompanyUser(BasePermission):
    """
    User must belong to an active company via CompanyMember.
    Uses request.tenant for resolution.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        tenant = getattr(request, "tenant", None)

        if not tenant or not tenant.company:
            return False

        return tenant.company.is_active


class IsSameCompany(BasePermission):
    """
    Object-level company isolation via TenantContext.
    """

    def has_object_permission(self, request, view, obj):
        tenant = getattr(request, "tenant", None)
        if not tenant or not tenant.company:
            return False
        return obj.company == tenant.company


class IsProjectMember(BasePermission):
    """
    Company membership should NOT automatically grant project access.
    Permission chain: IsAuthenticated → IsCompanyMember → IsProjectMember → RolePermission
    """

    def has_permission(self, request, view):
        # First check company membership
        tenant = getattr(request, "tenant", None)
        if not tenant or not tenant.company:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        project = obj.project if hasattr(obj, "project") else obj
        from project_members.models import ProjectMember

        return ProjectMember.objects.filter(
            project=project,
            user=request.user,
            is_active=True,
        ).exists()

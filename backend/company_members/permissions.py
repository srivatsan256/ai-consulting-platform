from rest_framework.permissions import BasePermission


class IsCompanyMember(BasePermission):
    """
    User must be an active member of the company.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        tenant = getattr(request, "tenant", None)
        if not tenant or not tenant.company:
            return False

        return True


class IsSameCompanyMember(BasePermission):
    """
    Object-level company membership check.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        company = obj.company if hasattr(obj, "company") else obj.company_id

        from .models import CompanyMember

        return CompanyMember.objects.filter(
            user=user,
            company_id=company.id if hasattr(company, "id") else company,
            is_active=True,
        ).exists()

from rest_framework.permissions import BasePermission


class IsCompanyMember(BasePermission):
    """
    Object-level check that the user is an active member of the company.
    """

    def has_object_permission(self, request, view, obj):
        return obj.members.filter(user=request.user, is_active=True).exists()


class IsCompanyOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user.is_superuser

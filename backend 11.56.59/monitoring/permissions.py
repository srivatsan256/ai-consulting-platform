from rest_framework.permissions import BasePermission


class IsMonitoringAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_staff

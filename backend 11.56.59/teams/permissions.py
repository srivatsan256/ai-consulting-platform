from rest_framework.permissions import BasePermission


class IsTeamMember(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.department.head == request.user

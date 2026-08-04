from rest_framework.permissions import BasePermission


class IsTaskAssignee(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.assigned_to == request.user

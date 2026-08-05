from rest_framework.permissions import BasePermission


class IsApprovalAssignee(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.assigned_to == request.user


class IsApprovalRequester(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.requested_by == request.user

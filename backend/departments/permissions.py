from rest_framework.permissions import BasePermission


class IsDepartmentHead(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.head == request.user

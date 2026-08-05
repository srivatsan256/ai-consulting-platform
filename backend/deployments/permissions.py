from rest_framework.permissions import BasePermission


class IsDeployer(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.deployed_by == request.user

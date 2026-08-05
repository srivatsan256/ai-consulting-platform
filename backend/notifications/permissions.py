from rest_framework.permissions import BasePermission


class IsNotificationRecipient(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.recipient == request.user

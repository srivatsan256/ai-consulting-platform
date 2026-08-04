from rest_framework.permissions import BasePermission


class IsAIAssessmentCreator(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user

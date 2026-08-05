from rest_framework.permissions import BasePermission


class IsReviewReviewer(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user

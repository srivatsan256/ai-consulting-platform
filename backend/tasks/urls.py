from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import TaskViewSet, TaskCommentViewSet, TaskAttachmentViewSet

router = DefaultRouter()

router.register(
    "",
    TaskViewSet,
    basename="task",
)

router.register(
    "comments",
    TaskCommentViewSet,
    basename="taskcomment",
)

router.register(
    "attachments",
    TaskAttachmentViewSet,
    basename="taskattachment",
)

urlpatterns = [
    path("", include(router.urls)),
]

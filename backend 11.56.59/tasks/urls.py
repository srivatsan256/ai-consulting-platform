from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import TaskViewSet, TaskCommentViewSet

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

urlpatterns = [
    path("", include(router.urls)),
]

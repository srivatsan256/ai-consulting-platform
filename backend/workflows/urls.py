from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    WorkflowViewSet,
    WorkflowExecutionViewSet,
    WorkflowHistoryViewSet,
)

router = DefaultRouter()

router.register(
    "",
    WorkflowViewSet,
    basename="workflow",
)

router.register(
    "executions",
    WorkflowExecutionViewSet,
    basename="workflowexecution",
)

router.register(
    "history",
    WorkflowHistoryViewSet,
    basename="workflowhistory",
)

urlpatterns = [
    path("", include(router.urls)),
]

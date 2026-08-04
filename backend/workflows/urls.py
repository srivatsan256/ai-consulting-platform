from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import WorkflowViewSet, WorkflowExecutionViewSet

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

urlpatterns = [
    path("", include(router.urls)),
]

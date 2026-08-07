from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import extend_schema # type: ignore

from .models import Workflow, WorkflowStep, WorkflowExecution
from .serializers import (
    WorkflowSerializer,
    WorkflowStepSerializer,
    WorkflowExecutionSerializer,
)
from .filters import WorkflowFilter
from core.tenant_scoping import TenantScopedViewSetMixin


class WorkflowViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = WorkflowSerializer

    queryset = Workflow.objects.select_related(
        "project",
        "created_by",
    ).prefetch_related("steps")

    filterset_class = WorkflowFilter

    search_fields = [
        "name",
        "description",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "name",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

    lookup_value_regex = r"[0-9]+"

    def get_queryset(self):
        return super().get_queryset().filter(
            project__is_active=True,
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        workflow = self.get_object()
        workflow.status = "active"
        workflow.save()
        return Response({"message": "Workflow activated."})

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        workflow = self.get_object()
        workflow.status = "inactive"
        workflow.save()
        return Response({"message": "Workflow deactivated."})

    @action(detail=True, methods=["post"])
    def add_step(self, request, pk=None):
        workflow = self.get_object()
        serializer = WorkflowStepSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workflow=workflow)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        operation_id="workflows_workflow_executions_list",
        summary="List executions for a workflow",
        responses={200: WorkflowExecutionSerializer(many=True)},
        tags=["workflows"],
    )
    @action(detail=True, methods=["get"], url_path="workflow-executions")
    def executions(self, request, pk=None):
        workflow = self.get_object()
        executions = workflow.executions.select_related("initiated_by")
        serializer = WorkflowExecutionSerializer(executions, many=True)
        return Response(serializer.data)


class WorkflowExecutionViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = WorkflowExecutionSerializer

    queryset = WorkflowExecution.objects.select_related(
        "workflow",
        "current_step",
        "initiated_by",
    )

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(
            initiated_by=self.request.user,
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        execution = self.get_object()
        execution.status = "completed"
        execution.completed_at = timezone.now()
        execution.save()
        return Response({"message": "Execution completed."})

    @action(detail=True, methods=["post"])
    def fail(self, request, pk=None):
        execution = self.get_object()
        execution.status = "failed"
        execution.save()
        return Response({"message": "Execution failed."})

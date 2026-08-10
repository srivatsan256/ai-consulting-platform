from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiTypes # type: ignore

from .models import Task, TaskComment, TaskAttachment
from .serializers import (
    TaskAttachmentSerializer,
    TaskDetailSerializer,
    TaskCommentSerializer,
)
from .filters import TaskFilter
from core.tenant_scoping import TenantScopedViewSetMixin


class TaskViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = TaskDetailSerializer

    queryset = Task.objects.select_related(
        "project",
        "parent",
        "assigned_to",
        "created_by",
    ).prefetch_related("subtasks")

    filterset_class = TaskFilter

    search_fields = [
        "title",
        "description",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "due_date",
        "priority",
        "status",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

    lookup_value_regex = r"[0-9]+"

    def _notify_assignee(self, task):
        if task.assigned_to is None:
            return
        from notifications.services.service import NotificationService

        NotificationService.notify(
            recipient=task.assigned_to,
            title=f"Task assigned: {task.title}",
            message=f"You have been assigned to task '{task.title}'.",
            notification_type="info",
            category="task",
            entity_type="task",
            entity_id=task.pk,
        )

    def perform_create(self, serializer):
        task = serializer.save()
        self._notify_assignee(task)

    def perform_update(self, serializer):
        task = serializer.save()
        self._notify_assignee(task)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = "done"
        task.completed_at = timezone.now()
        task.save()
        return Response({"message": "Task completed."})

    @extend_schema(
        operation_id="tasks_task_comments_list",
        summary="List or create comments for a task",
        request=TaskCommentSerializer,
        responses={200: TaskCommentSerializer(many=True), 201: TaskCommentSerializer},
        tags=["tasks"],
    )
    @action(detail=True, methods=["get", "post"], url_path="task-comments")
    def task_comments(self, request, pk=None):
        task = self.get_object()
        if request.method == "GET":
            comments = task.comments.select_related("author")
            serializer = TaskCommentSerializer(comments, many=True)
            return Response(serializer.data)
        serializer = TaskCommentSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get", "post"], url_path="attachments")
    def attachments(self, request, pk=None):
        task = self.get_object()
        if request.method == "GET":
            attachments = task.attachments.select_related("uploaded_by")
            serializer = TaskAttachmentSerializer(
                attachments,
                many=True,
                context={"request": request},
            )
            return Response(serializer.data)

        file_obj = request.FILES.get("file")
        if file_obj is None:
            return Response(
                {"detail": "A file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from file_management.services.storage import enforce_storage_quota

        tenant = getattr(request, "tenant", None)
        if tenant and tenant.company:
            enforce_storage_quota(tenant.company, file_obj.size or 0)

        attachment = TaskAttachment.objects.create(
            task=task,
            file=file_obj,
            original_name=file_obj.name,
            file_size=file_obj.size or 0,
            content_type=file_obj.content_type or "",
            uploaded_by=request.user,
        )
        return Response(
            TaskAttachmentSerializer(
                attachment,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


class TaskAttachmentViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = TaskAttachmentSerializer

    queryset = TaskAttachment.objects.select_related("task", "uploaded_by")

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(
            task__project__is_active=True,
        )


class TaskCommentViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = TaskCommentSerializer

    queryset = TaskComment.objects.select_related("author", "task")

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(
            task__project__is_active=True,
        ).select_related("author", "task")

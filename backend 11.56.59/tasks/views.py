from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiTypes

from .models import Task, TaskComment
from .serializers import TaskDetailSerializer, TaskCommentSerializer
from .filters import TaskFilter


class TaskViewSet(viewsets.ModelViewSet):

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

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = "done"
        task.completed_at = timezone.now()
        task.save()
        return Response({"message": "Task completed."})

    @extend_schema(
        operation_id="tasks_task_comments_list",
        summary="List comments for a task",
        responses={200: TaskCommentSerializer(many=True)},
        tags=["tasks"],
    )
    @action(detail=True, methods=["get"], url_path="task-comments")
    def list_comments(self, request, pk=None):
        task = self.get_object()
        comments = task.comments.select_related("author")
        serializer = TaskCommentSerializer(comments, many=True)
        return Response(serializer.data)

    @extend_schema(
        operation_id="tasks_task_comments_create",
        summary="Create a comment for a task",
        request=TaskCommentSerializer,
        responses={201: TaskCommentSerializer},
        tags=["tasks"],
    )
    @action(detail=True, methods=["post"], url_path="task-comments")
    def create_comment(self, request, pk=None):
        task = self.get_object()
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


class TaskCommentViewSet(viewsets.ModelViewSet):

    serializer_class = TaskCommentSerializer

    queryset = TaskComment.objects.select_related("author", "task")

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TaskComment.objects.filter(
            task__project__is_active=True,
        ).select_related("author", "task")

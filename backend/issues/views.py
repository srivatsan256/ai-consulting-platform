from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import Issue, IssueComment
from .serializers import IssueSerializer, IssueCommentSerializer
from .filters import IssueFilter
from core.tenant_scoping import TenantScopedViewSetMixin


class IssueViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = IssueSerializer

    queryset = Issue.objects.select_related(
        "project",
        "assigned_to",
        "reported_by",
    )

    filterset_class = IssueFilter

    search_fields = [
        "title",
        "description",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "priority",
        "status",
        "due_date",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        issue = self.get_object()
        issue.status = "resolved"
        issue.resolved_date = timezone.now()
        issue.resolution_notes = request.data.get(
            "resolution_notes", ""
        )
        issue.save()
        return Response({"message": "Issue resolved."})

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        issue = self.get_object()
        issue.status = "closed"
        issue.save()
        return Response({"message": "Issue closed."})

    @action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        issue = self.get_object()
        issue.status = "reopened"
        issue.save()
        return Response({"message": "Issue reopened."})

    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        issue = self.get_object()

        if request.method == "GET":
            comments = issue.comments.select_related("author")
            serializer = IssueCommentSerializer(comments, many=True)
            return Response(serializer.data)

        serializer = IssueCommentSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(issue=issue)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

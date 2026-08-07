from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import SecurityChecklist, VulnerabilityReport
from .serializers import SecurityChecklistSerializer, VulnerabilityReportSerializer
from .filters import SecurityChecklistFilter, VulnerabilityReportFilter
from core.tenant_scoping import TenantScopedViewSetMixin


class SecurityChecklistViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = SecurityChecklistSerializer

    queryset = SecurityChecklist.objects.select_related(
        "project",
        "assigned_to",
        "verified_by",
    )

    filterset_class = SecurityChecklistFilter

    search_fields = [
        "title",
        "description",
        "notes",
    ]

    ordering_fields = [
        "created_at",
        "due_date",
        "status",
        "category",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        checklist = self.get_object()
        checklist.status = "passed"
        checklist.verified_by = request.user
        checklist.completed_at = timezone.now()
        checklist.save()
        return Response({"message": "Checklist verified."})

    @action(detail=True, methods=["post"])
    def fail(self, request, pk=None):
        checklist = self.get_object()
        checklist.status = "failed"
        checklist.notes = request.data.get("notes", checklist.notes)
        checklist.save()
        return Response({"message": "Checklist failed."})


class VulnerabilityReportViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = VulnerabilityReportSerializer

    queryset = VulnerabilityReport.objects.select_related(
        "project",
        "reported_by",
    )

    filterset_class = VulnerabilityReportFilter

    search_fields = [
        "title",
        "description",
        "affected_component",
    ]

    ordering_fields = [
        "created_at",
        "severity",
        "status",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def mitigate(self, request, pk=None):
        report = self.get_object()
        report.status = "mitigated"
        report.mitigation = request.data.get("mitigation", "")
        report.save()
        return Response({"message": "Vulnerability mitigated."})

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        report = self.get_object()
        report.status = "resolved"
        report.resolved_date = timezone.now().date()
        report.save()
        return Response({"message": "Vulnerability resolved."})

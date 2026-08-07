from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import Approval
from .serializers import ApprovalSerializer
from .filters import ApprovalFilter
from core.tenant_scoping import TenantScopedViewSetMixin


class ApprovalViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = ApprovalSerializer

    queryset = Approval.objects.select_related(
        "project",
        "requested_by",
        "assigned_to",
    )

    filterset_class = ApprovalFilter

    search_fields = [
        "title",
        "description",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "status",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        approval = self.get_object()
        approval.status = "approved"
        approval.decision_date = timezone.now()
        approval.remarks = request.data.get("remarks", "")
        approval.save()
        return Response({"message": "Approval granted."})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        approval = self.get_object()
        approval.status = "rejected"
        approval.decision_date = timezone.now()
        approval.remarks = request.data.get("remarks", "")
        approval.save()
        return Response({"message": "Approval rejected."})

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        approval = self.get_object()
        approval.status = "cancelled"
        approval.save()
        return Response({"message": "Approval cancelled."})

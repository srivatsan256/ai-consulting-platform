from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import Risk
from .serializers import RiskSerializer
from .filters import RiskFilter
from core.tenant_scoping import TenantScopedViewSetMixin


class RiskViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = RiskSerializer

    queryset = Risk.objects.select_related(
        "project",
        "owner",
        "identified_by",
    )

    filterset_class = RiskFilter

    search_fields = [
        "title",
        "description",
        "mitigation_plan",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "severity",
        "probability",
        "status",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def mitigate(self, request, pk=None):
        risk = self.get_object()
        risk.status = "mitigated"
        risk.mitigation_plan = request.data.get(
            "mitigation_plan", risk.mitigation_plan
        )
        risk.save()
        return Response({"message": "Risk mitigated."})

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        risk = self.get_object()
        risk.status = "closed"
        risk.resolved_date = timezone.now().date()
        risk.save()
        return Response({"message": "Risk closed."})

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        risk = self.get_object()
        risk.status = "accepted"
        risk.save()
        return Response({"message": "Risk accepted."})

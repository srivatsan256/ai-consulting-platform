from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView

from core.constants import API_VERSION

from .models import MonitoringAlert, SystemMetric
from .serializers import MonitoringAlertSerializer, SystemMetricSerializer
from .filters import MonitoringAlertFilter, SystemMetricFilter
from core.tenant_scoping import TenantScopedViewSetMixin


class HealthCheckAPIView(APIView):
    """Unauthenticated liveness/readiness probe for load balancers."""

    permission_classes = [AllowAny]

    def get(self, request):
        db_status = "ok"
        try:
            from django.db import connection

            connection.ensure_connection()
        except Exception:
            db_status = "error"

        ok = db_status == "ok"
        return Response(
            {
                "status": "ok" if ok else "degraded",
                "service": "ai-consulting-platform",
                "version": API_VERSION,
                "database": db_status,
                "time": timezone.now().isoformat(),
            },
            status=status.HTTP_200_OK if ok else status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class MonitoringAlertViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = MonitoringAlertSerializer

    queryset = MonitoringAlert.objects.select_related(
        "project",
        "acknowledged_by",
    )

    filterset_class = MonitoringAlertFilter

    search_fields = [
        "title",
        "message",
        "source",
    ]

    ordering_fields = [
        "created_at",
        "severity",
        "status",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.status = "acknowledged"
        alert.acknowledged_by = request.user
        alert.save()
        return Response({"message": "Alert acknowledged."})

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.status = "resolved"
        alert.resolved_at = timezone.now()
        alert.save()
        return Response({"message": "Alert resolved."})


class SystemMetricViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = SystemMetricSerializer

    queryset = SystemMetric.objects.select_related("project")

    filterset_class = SystemMetricFilter

    permission_classes = [IsAuthenticated]

    ordering_fields = [
        "recorded_at",
        "metric_name",
    ]

    ordering = ["-recorded_at"]

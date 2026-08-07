from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import DashboardWidget
from .serializers import DashboardWidgetSerializer
from .filters import DashboardWidgetFilter
from core.tenant_scoping import TenantScopedViewSetMixin


class DashboardWidgetViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = DashboardWidgetSerializer

    queryset = DashboardWidget.objects.select_related(
        "owner",
        "project",
    )

    filterset_class = DashboardWidgetFilter

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(
            owner=self.request.user,
        )

    ordering_fields = [
        "position",
        "created_at",
    ]

    ordering = ["position"]

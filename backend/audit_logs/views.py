from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import AuditLog
from .serializers import AuditLogSerializer
from .filters import AuditLogFilter
from core.tenant_scoping import TenantScopedViewSetMixin


class AuditLogViewSet(TenantScopedViewSetMixin, viewsets.ReadOnlyModelViewSet):

    serializer_class = AuditLogSerializer

    queryset = AuditLog.objects.select_related("user")

    filterset_class = AuditLogFilter

    search_fields = [
        "entity_name",
        "user__email",
    ]

    ordering_fields = [
        "timestamp",
        "action",
    ]

    ordering = ["-timestamp"]

    permission_classes = [IsAuthenticated]

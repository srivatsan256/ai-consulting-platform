from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import DocumentTemplate
from .serializers import DocumentTemplateSerializer
from .filters import DocumentTemplateFilter
from core.tenant_scoping import TenantScopedViewSetMixin


class DocumentTemplateViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = DocumentTemplateSerializer

    queryset = DocumentTemplate.objects.select_related(
        "project",
        "created_by",
    )

    filterset_class = DocumentTemplateFilter

    search_fields = [
        "name",
        "description",
    ]

    ordering_fields = [
        "name",
        "created_at",
        "updated_at",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        self._validate_tenant_scoped_fks(serializer.validated_data)
        project = serializer.validated_data.get("project")
        file_obj = serializer.validated_data.get("file")
        if project is not None:
            from file_management.services.storage import (
                enforce_plan_storage_quota,
                enforce_storage_quota,
            )

            size = getattr(file_obj, "size", 0) or 0
            enforce_storage_quota(project.company, size)
            enforce_plan_storage_quota(project.company, size)
        serializer.save()

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import ArchitectureDiagram, TechnologyStack
from .serializers import ArchitectureDiagramSerializer, TechnologyStackSerializer
from .filters import ArchitectureDiagramFilter, TechnologyStackFilter
from core.tenant_scoping import TenantScopedViewSetMixin


class ArchitectureDiagramViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = ArchitectureDiagramSerializer

    queryset = ArchitectureDiagram.objects.select_related(
        "project",
        "created_by",
    )

    filterset_class = ArchitectureDiagramFilter

    search_fields = [
        "title",
        "description",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "category",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]


class TechnologyStackViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = TechnologyStackSerializer

    queryset = TechnologyStack.objects.select_related("project")

    filterset_class = TechnologyStackFilter

    search_fields = [
        "name",
        "purpose",
    ]

    ordering_fields = [
        "name",
        "category",
        "created_at",
    ]

    ordering = ["name"]

    permission_classes = [IsAuthenticated]

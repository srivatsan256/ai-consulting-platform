from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import ProjectMember
from .serializers import ProjectMemberSerializer
from .filters import ProjectMemberFilter
from core.tenant_scoping import TenantScopedViewSetMixin


class ProjectMemberViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    queryset = ProjectMember.objects.select_related(
        "project",
        "user",
        "role"
    )
    serializer_class = ProjectMemberSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ProjectMemberFilter
    search_fields = ["user__email", "project__project_name"]
    ordering_fields = ["joined_at", "created_at"]

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import Deployment
from .serializers import DeploymentSerializer
from .filters import DeploymentFilter
from core.tenant_scoping import TenantScopedViewSetMixin


class DeploymentViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = DeploymentSerializer

    queryset = Deployment.objects.select_related(
        "project",
        "deployed_by",
        "approved_by",
    )

    filterset_class = DeploymentFilter

    search_fields = [
        "title",
        "description",
        "version",
        "changelog",
    ]

    ordering_fields = [
        "created_at",
        "deployed_at",
        "environment",
        "status",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def deploy(self, request, pk=None):
        deployment = self.get_object()
        deployment.status = "in_progress"
        deployment.save()
        return Response({"message": "Deployment started."})

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        deployment = self.get_object()
        deployment.status = "completed"
        deployment.deployed_at = timezone.now()
        deployment.save()
        return Response({"message": "Deployment completed."})

    @action(detail=True, methods=["post"])
    def rollback(self, request, pk=None):
        deployment = self.get_object()
        deployment.status = "rolled_back"
        deployment.rollback_notes = request.data.get("rollback_notes", "")
        deployment.save()
        return Response({"message": "Deployment rolled back."})

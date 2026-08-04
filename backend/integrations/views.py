from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Integration
from .serializers import IntegrationSerializer
from .filters import IntegrationFilter


class IntegrationViewSet(viewsets.ModelViewSet):

    serializer_class = IntegrationSerializer

    queryset = Integration.objects.select_related(
        "project",
        "created_by",
    )

    filterset_class = IntegrationFilter

    search_fields = [
        "name",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "name",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        integration = self.get_object()
        integration.status = "active"
        integration.save()
        return Response({"message": "Integration activated."})

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        integration = self.get_object()
        integration.status = "inactive"
        integration.save()
        return Response({"message": "Integration deactivated."})

    @action(detail=True, methods=["post"])
    def sync(self, request, pk=None):
        integration = self.get_object()
        integration.status = "active"
        integration.error_message = ""
        integration.save()
        return Response({"message": "Sync initiated."})

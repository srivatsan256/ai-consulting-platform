from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Permission
from .serializers import PermissionSerializer
from .filters import PermissionFilter


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.select_related("role")
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PermissionFilter
    ordering_fields = ["feature", "created_at"]

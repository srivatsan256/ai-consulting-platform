from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Role
from .serializers import RoleSerializer
from .filters import RoleFilter


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = RoleFilter
    search_fields = ["display_name", "role_key"]
    ordering_fields = ["display_name", "created_at"]
    ordering = ["display_name"]

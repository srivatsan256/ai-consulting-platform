from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Team
from .serializers import TeamSerializer


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        tenant = getattr(self.request, "tenant", None)
        if tenant and tenant.company:
            return queryset.filter(department__company=tenant.company)
        return queryset.none()

    queryset = Team.objects.select_related("department", "department__company")

    filterset_fields = ["department", "is_active"]
    search_fields = ["team_name", "description"]
    ordering_fields = ["team_name", "created_at"]
    ordering = ["team_name"]

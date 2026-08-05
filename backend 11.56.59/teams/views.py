from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Team
from .serializers import TeamSerializer


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    queryset = Team.objects.select_related("department", "department__company")

    filterset_fields = ["department", "is_active"]
    search_fields = ["team_name", "description"]
    ordering_fields = ["team_name", "created_at"]
    ordering = ["team_name"]

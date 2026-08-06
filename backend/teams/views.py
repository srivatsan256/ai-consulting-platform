from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Team, TeamMember
from .serializers import TeamSerializer, TeamMemberSerializer


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    lookup_value_regex = r"[0-9]+"

    def get_queryset(self):
        queryset = super().get_queryset()
        tenant = getattr(self.request, "tenant", None)
        if tenant and tenant.company:
            return queryset.filter(department__company=tenant.company)
        return queryset.none()

    def perform_create(self, serializer):
        from rest_framework.exceptions import ValidationError

        tenant = getattr(self.request, "tenant", None)
        department = serializer.validated_data.get("department")
        if (
            tenant
            and tenant.company
            and department
            and department.company_id != tenant.company.id
        ):
            raise ValidationError(
                {"department": "Department must belong to your company."}
            )
        serializer.save()

    queryset = Team.objects.select_related("department", "department__company")

    filterset_fields = ["department", "is_active"]
    search_fields = ["team_name", "description"]
    ordering_fields = ["team_name", "created_at"]
    ordering = ["team_name"]


class TeamMemberViewSet(viewsets.ModelViewSet):
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["team", "role", "user"]
    lookup_value_regex = r"[0-9]+"

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        queryset = TeamMember.objects.select_related(
            "team__department__company",
            "user",
        )
        if tenant and tenant.company:
            return queryset.filter(
                team__department__company=tenant.company,
            )
        return queryset.none()

    def perform_create(self, serializer):
        from rest_framework.exceptions import ValidationError

        tenant = getattr(self.request, "tenant", None)
        team = serializer.validated_data.get("team")
        if (
            tenant
            and tenant.company
            and team
            and team.department.company_id != tenant.company.id
        ):
            raise ValidationError(
                {"team": "Team must belong to your company."}
            )
        serializer.save()

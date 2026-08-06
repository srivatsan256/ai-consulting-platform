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

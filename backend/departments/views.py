from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Department
from .serializers import DepartmentDetailSerializer
from .filters import DepartmentFilter


class DepartmentViewSet(viewsets.ModelViewSet):

    serializer_class = DepartmentDetailSerializer

    queryset = Department.objects.select_related(
        "company",
        "head",
        "created_by",
    )

    filterset_class = DepartmentFilter

    search_fields = [
        "name",
        "code",
        "description",
    ]

    ordering_fields = [
        "name",
        "code",
        "created_at",
        "updated_at",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        tenant = getattr(self.request, "tenant", None)
        if tenant and tenant.company:
            return queryset.filter(company=tenant.company)
        return queryset.none()

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        serializer.save(
            company=tenant.company if tenant and tenant.company else None,
            created_by=self.request.user,
        )

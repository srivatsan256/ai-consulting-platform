from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Department, DepartmentMember
from .serializers import (
    DepartmentDetailSerializer,
    DepartmentMemberSerializer,
)
from .filters import DepartmentFilter
from core.rbac.department_permissions import CanManageDepartmentMembers


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


class DepartmentMemberViewSet(viewsets.ModelViewSet):
    """
    Manage department membership (department-based access).

    Read actions are available to any active company member. Create, update
    and delete require a company admin/super admin or the department head.
    GET /api/departments/members/mine/ returns the acting user's departments.
    """

    serializer_class = DepartmentMemberSerializer
    permission_classes = [IsAuthenticated]
    lookup_value_regex = r"[0-9]+"

    queryset = DepartmentMember.objects.select_related(
        "department__company",
        "user",
    )

    filterset_fields = ["department", "user", "is_active"]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        queryset = super().get_queryset()
        if tenant and tenant.company:
            return queryset.filter(department__company=tenant.company)
        return queryset.none()

    def get_permissions(self):
        permissions = [IsAuthenticated()]
        if self.action in ("create", "update", "partial_update", "destroy"):
            permissions.append(CanManageDepartmentMembers())
        return permissions

    @action(detail=False, methods=["get"], url_path="mine")
    def mine(self, request):
        """
        Return the departments the acting user is a member of.
        GET /api/departments/members/mine/
        """
        rows = self.get_queryset().filter(
            user=request.user,
            is_active=True,
        )
        return Response(DepartmentMemberSerializer(rows, many=True).data)

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        department = serializer.validated_data.get("department")
        if tenant is None or department is None or department.company_id != tenant.company.id:
            from rest_framework.exceptions import ValidationError

            raise ValidationError(
                {"department": "Department must belong to your company."}
            )
        serializer.save()

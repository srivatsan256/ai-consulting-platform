from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from roles.models import Role
from roles.serializers import (
    AssignRoleSerializer,
    MyRoleSerializer,
    RoleAssignmentSerializer,
    RoleSerializer,
)
from roles.services.service import RoleAssignmentService
from roles.filters import RoleFilter
from core.rbac.permissions import is_manager_role


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = RoleFilter
    search_fields = ["display_name", "role_key"]
    ordering_fields = ["display_name", "created_at"]
    ordering = ["display_name"]
    lookup_value_regex = r"[0-9]+"

    @action(detail=False, methods=["post"], url_path="assign")
    def assign(self, request):
        """
        Assign a role to a user in the tenant company.
        POST /api/roles/assign/
        Payload: {"user": <id>, "role": <id>, "company": <id, optional>}
        """
        serializer = AssignRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant = getattr(request, "tenant", None)
        company = serializer.validated_data.get("company")
        if company is not None:
            from companies.models import Company

            company = Company.objects.filter(pk=company).first()
            if company is None or tenant is None or company != tenant.company:
                return Response(
                    {"detail": "Company is outside your tenant."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif tenant is not None:
            company = tenant.company
        else:
            return Response(
                {"detail": "No active company."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        role = Role.objects.filter(pk=serializer.validated_data["role"]).first()
        target_user = User.objects.filter(pk=serializer.validated_data["user"]).first()

        if role is None or not role.is_active:
            return Response(
                {"role": "Role must be active and valid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if target_user is None:
            return Response(
                {"user": "User does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            assignment = RoleAssignmentService.assign(
                actor=request.user,
                user=target_user,
                company=company,
                role=role,
            )
        except ValidationError as exc:
            return Response(
                exc.detail, status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionDenied as exc:
            return Response(
                exc.detail, status=status.HTTP_403_FORBIDDEN
            )

        if assignment is None:
            return Response(
                {"detail": "User already holds this role."},
                status=status.HTTP_200_OK,
            )

        return Response(
            RoleAssignmentSerializer(assignment).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], url_path="mine")
    def mine(self, request):
        """
        Return the acting user's role and feature permissions for the
        tenant company.
        GET /api/roles/mine/
        """
        from core.rbac.role_resolver import my_role_context

        context = my_role_context(request)
        if context is None:
            return Response(
                {"detail": "No active membership."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(MyRoleSerializer(context).data)

    @action(detail=False, methods=["get"], url_path="assignments")
    def assignments(self, request):
        """
        List the role-assignment audit trail for the tenant company.
        GET /api/roles/assignments/
        """
        tenant = getattr(request, "tenant", None)
        role = getattr(tenant, "role", None)

        if not is_manager_role(role):
            return Response(
                {"detail": "Only a company admin or super admin can view assignments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        history = RoleAssignmentService.history_for_company(tenant.company)
        return Response(RoleAssignmentSerializer(history, many=True).data)

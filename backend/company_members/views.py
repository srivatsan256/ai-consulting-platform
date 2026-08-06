from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CompanyMember
from .serializers import CompanyMemberSerializer, SwitchCompanySerializer
from .permissions import IsCompanyMember


class CompanyMemberViewSet(viewsets.ModelViewSet):
    """
    Manage company memberships.
    Switch company is handled via POST /api/memberships/switch/
    """

    serializer_class = CompanyMemberSerializer
    permission_classes = [IsAuthenticated]
    queryset = CompanyMember.objects.none()

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser: # type: ignore
            return CompanyMember.objects.all()
        return CompanyMember.objects.for_user(user) # type: ignore

    def perform_create(self, serializer):
        company = serializer.validated_data.get("company")
        target_user = serializer.validated_data.get("user")
        user = self.request.user

        if company is not None:
            from subscriptions.services.usage_service import QuotaService

            if QuotaService.get_active_subscription(company) is not None:
                QuotaService.check(
                    company,
                    "users",
                    CompanyMember.objects.filter(
                        company=company,
                        is_active=True,
                    ).count(),
                )

        can_manage = bool(user.is_superuser)  # type: ignore
        if not can_manage and company is not None:
            existing = (
                CompanyMember.objects.filter(
                    user=user,
                    company=company,
                    is_active=True,
                )
                .select_related("role")
                .first()
            )
            can_manage = existing is not None and existing.role is not None and existing.role.role_key in (
                "super_admin",
                "company_admin",
            )

        if target_user is None or not can_manage:
            serializer.save(user=user)
        else:
            serializer.save(user=target_user)

    @action(detail=False, methods=["post"], url_path="switch")
    def switch_company(self, request):
        """
        Switch active company.
        POST /api/memberships/switch/
        """
        serializer = SwitchCompanySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        company_id = serializer.validated_data["company_id"]
        user = request.user

        try:
            membership = CompanyMember.objects.get(
                user=user,
                company_id=company_id,
                is_active=True,
            )
        except CompanyMember.DoesNotExist:
            return Response(
                {"detail": "You are not a member of this company."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Set as primary
        CompanyMember.objects.set_primary(user, membership.company) # type: ignore

        # Update JWT claim or return new token
        # For now, return success with updated membership
        return Response(
            {
                "detail": "Company switched successfully.",
                "company_id": membership.company_id, # type: ignore
                "company_name": membership.company.company_name,
                "role": membership.role.display_name,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="current")
    def current_membership(self, request):
        """
        Get current active membership.
        GET /api/memberships/current/
        """
        tenant = getattr(request, "tenant", None)
        if not tenant or not tenant.membership:
            return Response(
                {"detail": "No active membership."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CompanyMemberSerializer(tenant.membership)
        return Response(serializer.data)

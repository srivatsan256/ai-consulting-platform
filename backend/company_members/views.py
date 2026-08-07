from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import CompanyMember, UserInvitation
from .serializers import (
    AcceptInvitationSerializer,
    CompanyMemberSerializer,
    InviteUserSerializer,
    SwitchCompanySerializer,
    UserInvitationSerializer,
)
from .permissions import IsCompanyMember
from .services.service import InvitationService


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
            if (
                not can_manage
                and existing is not None
                and existing.role is not None
            ):
                # Non-managers cannot grant themselves an arbitrary role; the
                # membership is recorded with their current role.
                serializer.validated_data["role"] = existing.role
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

    # ------------------------------------------------------------------
    # Invitations
    # ------------------------------------------------------------------

    def _tenant_company(self):
        tenant = getattr(self.request, "tenant", None)
        return getattr(tenant, "company", None)

    def _can_manage(self, company):
        user = self.request.user
        if getattr(user, "is_superuser", False):
            return True
        if company is None:
            return False
        from core.rbac.permissions import is_manager_role

        membership = (
            CompanyMember.objects.filter(
                user=user,
                company=company,
                is_active=True,
            )
            .select_related("role")
            .first()
        )
        return membership is not None and is_manager_role(membership.role)

    def _require_manager(self):
        company = self._tenant_company()
        if not self._can_manage(company):
            raise PermissionDenied(
                "Only company managers can manage invitations."
            )
        return company

    @action(detail=False, methods=["post"], url_path="invite", url_name="invite")
    def invite_user(self, request):
        """
        Invite a user to the acting company.
        POST /api/memberships/invite/
        """
        company = self._require_manager()

        serializer = InviteUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invitation = InvitationService(request.user).create_invitation(
            email=serializer.validated_data["email"],
            company=company,
            role=serializer.validated_data["role"],
            department=serializer.validated_data.get("department"),
        )
        return Response(
            UserInvitationSerializer(invitation).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], url_path="invitations", url_name="invitations")
    def list_invitations(self, request):
        """
        List invitations for the acting company.
        GET /api/memberships/invitations/
        """
        company = self._require_manager()

        queryset = UserInvitation.objects.filter(company=company)
        serializer = UserInvitationSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="invitations/accept",
        url_name="accept-invitation",
        permission_classes=[AllowAny],
    )
    def accept_invitation(self, request):
        """
        Accept an invitation and create the user account.
        POST /api/memberships/invitations/accept/
        """
        serializer = AcceptInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, invitation = InvitationService().accept_invitation(
            token=serializer.validated_data["token"],
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data["last_name"],
            password=serializer.validated_data["password"],
        )

        from authentication.serializers import CurrentUserSerializer
        from authentication.services.service import AuthenticationService

        tokens = AuthenticationService(request).create_tokens(user)
        return Response(
            {
                "success": True,
                "message": "Invitation accepted. Account created.",
                "refresh": tokens["refresh"],
                "access": tokens["access"],
                "user": CurrentUserSerializer(user).data,
                "company": {
                    "id": invitation.company_id,
                    "name": invitation.company.company_name,
                },
                "role": {
                    "id": invitation.role_id,
                    "name": invitation.role.display_name,
                    "key": invitation.role.role_key,
                },
            },
            status=status.HTTP_201_CREATED,
        )

from django.contrib.auth import update_session_auth_hash
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore

from audit_logs.services.audit_log_service import AuditLogService
from authentication.models import UserSession
from company_members.models import CompanyMember


class AuthenticationService:
    """
    Handles authentication-related business logic.
    """

    def __init__(self, request):
        self.request = request
        self.user = request.user

    # ---------------------------------------------------------------------
    # User
    # ---------------------------------------------------------------------

    def get_current_user(self):
        if not self.user.is_authenticated:
            raise PermissionDenied("Authentication required.")
        return self.user

    # ---------------------------------------------------------------------
    # Password
    # ---------------------------------------------------------------------

    @transaction.atomic
    def change_password(self, serializer):
        """
        Change authenticated user's password.
        """

        user = self.user

        user.set_password(serializer.validated_data["new_password"])
        user.save(
            update_fields=[
                "password",
                "password_changed_at",
                "password_version",
            ]
        )

        update_session_auth_hash(self.request, user)

        from authentication.services.session_service import SessionService

        SessionService.revoke_all_sessions(user=user)

        AuditLogService.log(
            company=None,
            user=user,
            action="PASSWORD_CHANGED",
            resource="User",
            resource_id=str(user.pk),
            metadata={
                "via": "change_password",
            },
        )

        return user

    # ---------------------------------------------------------------------
    # Logout
    # ---------------------------------------------------------------------

    def logout(self, refresh_token):
        """
        Blacklist refresh token, revoke the session and record logout.
        """

        from authentication.services.login_history import LoginHistoryService

        token = RefreshToken(refresh_token)
        token.blacklist()

        UserSession.objects.filter(
            refresh_token_jti=token["jti"],
            is_active=True,
        ).update(
            is_active=False,
            revoked_at=timezone.now(),
            updated_at=timezone.now(),
        )

        LoginHistoryService.record_logout(
            request=self.request,
            user=self.user,
        )

        return True

    # ---------------------------------------------------------------------
    # Company
    # ---------------------------------------------------------------------

    def switch_company(self, company_id):
        """
        Validate user membership.
        Returns membership used by the view to generate JWT.
        """

        membership = (
            CompanyMember.objects
            .select_related("company", "role")
            .filter(
                user=self.user,
                company_id=company_id,
                is_active=True,
            )
            .first()
        )

        if membership is None:
            raise NotFound("Company membership not found.")

        CompanyMember.objects.filter(
            user=self.user,
            is_primary=True,
        ).update(is_primary=False)

        membership.is_primary = True
        membership.save(update_fields=["is_primary"])

        return membership

    # ---------------------------------------------------------------------
    # Membership
    # ---------------------------------------------------------------------

    def get_memberships(self):
        """
        Return all active company memberships.
        """

        return (
            CompanyMember.objects
            .select_related("company", "role")
            .filter(
                user=self.user,
                is_active=True,
            )
            .order_by("company__company_name")
        )

    def get_primary_membership(self):
        """
        Return primary membership.
        """

        membership = (
            CompanyMember.objects
            .select_related("company", "role")
            .filter(
                user=self.user,
                is_active=True,
                is_primary=True,
            )
            .first()
        )

        if membership:
            return membership

        return (
            CompanyMember.objects
            .select_related("company", "role")
            .filter(
                user=self.user,
                is_active=True,
            )
            .first()
        )

    # ---------------------------------------------------------------------
    # JWT
    # ---------------------------------------------------------------------

    def create_tokens(self, user):
        """
        Generate Refresh and Access tokens.
        """

        refresh = RefreshToken.for_user(user)

        membership = (
            CompanyMember.objects
            .select_related("company", "role")
            .filter(
                user=user,
                is_active=True,
                is_primary=True,
            )
            .first()
        )

        if membership:
            refresh["company_id"] = membership.company_id
            refresh["role_id"] = membership.role_id

        refresh["pwd_ver"] = getattr(user, "password_version", 0)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

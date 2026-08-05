from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from audit_logs.services.audit_log_service import AuditLogService
from authentication.models import UserSession


class SessionService:
    """
    Service responsible for managing user sessions.

    Responsibilities:
        - Create session
        - Update activity
        - Revoke session
        - Revoke other sessions
        - Cleanup expired sessions
    """

    @staticmethod
    @transaction.atomic
    def create_session(
        *,
        user: Any,
        company: Any,
        refresh_token_jti: str,
        expires_at,
        ip_address: str,
        user_agent: str,
        browser: str = "",
        operating_system: str = "",
        device_name: str = "",
        device_type: str = "",
    ) -> UserSession:
        """
        Create a new authenticated session.
        """

        session = UserSession.objects.create(
            company=company,
            user=user,
            refresh_token_jti=refresh_token_jti,
            device_name=device_name,
            device_type=device_type,
            browser=browser,
            operating_system=operating_system,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
        )

        AuditLogService.log(
            company=company,
            user=user,
            action="SESSION_CREATED",
            resource="UserSession",
            resource_id=str(session.id),
            metadata={
                "ip_address": ip_address,
                "browser": browser,
                "device": device_name,
            },
        )

        return session

    @staticmethod
    @transaction.atomic
    def update_activity(session: UserSession) -> UserSession:
        """
        Update session activity timestamp.
        """

        session.last_activity_at = timezone.now()
        session.save(
            update_fields=[
                "last_activity_at",
                "updated_at",
            ]
        )

        return session

    @staticmethod
    @transaction.atomic
    def revoke_session(
        *,
        session: UserSession,
        revoked_by: Any,
    ) -> UserSession:
        """
        Revoke a single session.
        """

        if not session.is_active:
            return session

        session.is_active = False
        session.revoked_at = timezone.now()

        session.save(
            update_fields=[
                "is_active",
                "revoked_at",
                "updated_at",
            ]
        )

        AuditLogService.log(
            company=session.company,
            user=revoked_by,
            action="SESSION_REVOKED",
            resource="UserSession",
            resource_id=str(session.id),
            metadata={
                "target_user": session.user.id,
            },
        )

        return session

    @staticmethod
    @transaction.atomic
    def revoke_other_sessions(
        *,
        current_session: UserSession,
    ) -> int:
        """
        Revoke all sessions except the current one.

        Returns
        -------
        int
            Number of revoked sessions.
        """

        sessions = UserSession.objects.filter(
            company=current_session.company,
            user=current_session.user,
            is_active=True,
        ).exclude(
            id=current_session.id,
        )

        revoked_count = sessions.update(
            is_active=False,
            revoked_at=timezone.now(),
            updated_at=timezone.now(),
        )

        AuditLogService.log(
            company=current_session.company,
            user=current_session.user,
            action="ALL_OTHER_SESSIONS_REVOKED",
            resource="UserSession",
            resource_id=str(current_session.id),
            metadata={
                "revoked_sessions": revoked_count,
            },
        )

        return revoked_count

    @staticmethod
    @transaction.atomic
    def revoke_all_sessions(*, user: Any) -> int:
        """
        Revoke every active session for a user.

        Used after a password change or reset so all logged-in devices
        are signed out.

        Returns
        -------
        int
            Number of revoked sessions.
        """

        count = UserSession.objects.filter(
            user=user,
            is_active=True,
        ).update(
            is_active=False,
            revoked_at=timezone.now(),
            updated_at=timezone.now(),
        )

        AuditLogService.log(
            company=None,
            user=user,
            action="SESSIONS_REVOKED",
            resource="UserSession",
            metadata={
                "revoked_sessions": count,
                "reason": "password_changed",
            },
        )

        return count

    @staticmethod
    @transaction.atomic
    def cleanup_expired_sessions() -> int:
        """
        Cleanup expired sessions.

        Returns
        -------
        int
            Number of expired sessions cleaned.
        """

        expired_sessions = UserSession.objects.filter(
            expires_at__lte=timezone.now(),
            is_active=True,
        )

        count = expired_sessions.update(
            is_active=False,
            revoked_at=timezone.now(),
            updated_at=timezone.now(),
        )

        return count

    @staticmethod
    def get_active_sessions(*, user: Any, company: Any = None):
        """
        Return active sessions for a user.
        """

        company = company or getattr(user, "company", None)

        return (
            UserSession.objects.active()
            .filter(
                company=company,
                user=user,
            )
            .order_by("-last_activity_at")
        )

    @staticmethod
    def get_session(
        *,
        session_id,
        user: Any,
        company: Any = None,
    ) -> UserSession:
        """
        Return a user's session.

        Raises
        ------
        UserSession.DoesNotExist
        """

        company = company or getattr(user, "company", None)

        return UserSession.objects.get(
            id=session_id,
            company=company,
            user=user,
        )

    @staticmethod
    def is_current_session(
        *,
        session: UserSession,
        refresh_token_jti: str,
    ) -> bool:
        """
        Check whether a session is the current authenticated session.
        """

        return session.refresh_token_jti == refresh_token_jti
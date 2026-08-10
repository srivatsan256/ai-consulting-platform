"""
Custom JWT authentication and refresh serializers.

JWTs are stateless, so SimpleJWT alone cannot revoke tokens after a password
change or reset. These classes compare the token `pwd_ver` claim against the
user's `password_version` and reject any token carrying a stale version. The
version (not the second-granularity `iat` timestamp) is authoritative because
a password can be changed in the same second it was set.
"""

from __future__ import annotations

from datetime import datetime, timezone as dt_timezone

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication  # type: ignore
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError  # type: ignore
from rest_framework_simplejwt.serializers import TokenRefreshSerializer  # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore

from authentication.models import UserSession

User = get_user_model()


def _token_has_current_password_version(validated_token, user) -> bool:
    """
    Return True when the token carries the user's current password version.

    Tokens issued before the password last changed carry a stale version and
    are considered invalid.
    """
    expected = getattr(user, "password_version", 0)
    claimed = validated_token.get("pwd_ver", 0)
    return claimed == expected


class CustomJWTAuthentication(JWTAuthentication):
    """
    JWTAuthentication that rejects tokens issued before a password change.
    """

    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        if not _token_has_current_password_version(validated_token, user):
            raise InvalidToken("Token invalidated by password change.")

        return user

    def authenticate(self, request):
        """
        Authenticate the request and attach the resolved tenant context.

        ``TenantMiddleware`` runs before DRF authentication, so it cannot
        resolve a tenant for token-authenticated requests. Resolve it here
        (after the user is known) so ``request.tenant`` is available to
        permissions, views and services.

        The ``X-Company-ID`` header overrides the token's ``company_id``
        claim, letting multi-company users address another company without
        re-login.
        """
        result = super().authenticate(request)

        if result is not None:
            user, validated_token = result
            from core.services.tenant_resolution_service import (
                COMPANY_ID_HEADER,
                TenantResolutionService,
            )

            company_id = validated_token.get("company_id")
            header_value = request.headers.get(COMPANY_ID_HEADER)
            if header_value:
                try:
                    company_id = int(header_value)
                except (TypeError, ValueError):
                    pass

            request.tenant = TenantResolutionService().resolve_for_user(
                user=user,
                company_id=company_id,
            )

        return result


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """
    TokenRefreshSerializer that rejects refresh tokens issued before a
    password change and keeps the UserSession in sync with token rotation.
    """

    def validate(self, attrs):
        refresh = RefreshToken(attrs["refresh"])

        user_id = refresh.get("user_id")
        user = (
            User.objects.filter(pk=user_id)
            .only("id", "is_active", "password_version")
            .first()
        )

        if user is None or not user.is_active:
            raise InvalidToken("Token is invalid or expired.")

        if not _token_has_current_password_version(refresh, user):
            raise InvalidToken("Token invalidated by password change.")

        old_jti = refresh["jti"]

        data = super().validate(attrs)

        new_refresh = data.get("refresh")

        if new_refresh:
            try:
                rotated = RefreshToken(new_refresh)
                UserSession.objects.filter(
                    refresh_token_jti=old_jti,
                    is_active=True,
                ).update(
                    refresh_token_jti=rotated["jti"],
                    expires_at=datetime.fromtimestamp(
                        rotated["exp"],
                        tz=dt_timezone.utc,
                    ),
                    last_activity_at=timezone.now(),
                    updated_at=timezone.now(),
                )
            except TokenError:
                pass

        return data

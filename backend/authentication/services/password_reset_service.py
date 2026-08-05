"""
Password reset service.

Handles password reset OTP generation/verification and password reset confirmation.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta
from typing import Final

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)

from authentication.models import PasswordResetOtp

User = get_user_model()


class PasswordResetService:
    """
    Service responsible for password reset operations.
    """

    _token_generator: Final = PasswordResetTokenGenerator()

    OTP_TTL_SECONDS: Final = 10 * 60
    OTP_MAX_ATTEMPTS: Final = 5

    @staticmethod
    def _hash_otp(otp: str) -> str:
        """
        Return the SHA-256 hex digest of an OTP.
        """
        return hashlib.sha256(otp.encode()).hexdigest()

    @staticmethod
    def _generate_otp() -> str:
        """
        Generate a cryptographically secure 6-digit OTP.
        """
        return "{:06d}".format(secrets.randbelow(1_000_000))

    @classmethod
    def request_password_reset_otp(cls, email: str) -> None:
        """
        Generate and send a 6-digit password reset OTP by email.

        Never reveals whether the email exists.
        """
        user = (
            User.objects.filter(email__iexact=email, is_active=True)
            .only("id", "email")
            .first()
        )

        if not user:
            return

        normalized_email = email.strip().lower()
        otp = cls._generate_otp()

        # Invalidate any outstanding OTPs for this email.
        PasswordResetOtp.objects.filter(
            email=normalized_email,
            is_used=False,
        ).update(expires_at=timezone.now())

        PasswordResetOtp.objects.create(
            user=user,
            email=normalized_email,
            otp_hash=cls._hash_otp(otp),
            expires_at=timezone.now()
            + timedelta(seconds=cls.OTP_TTL_SECONDS),
        )

        context = {
            "user": user,
            "otp": otp,
            "expiry_minutes": cls.OTP_TTL_SECONDS // 60,
        }

        subject = "Your Password Reset Code"

        message = render_to_string(
            "emails/password_reset_otp.txt",
            context,
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email], # type: ignore
            fail_silently=False,
        )

    @classmethod
    def verify_otp(cls, email: str, otp: str) -> tuple[str, str]:
        """
        Validate an OTP and return (uid, token) for the confirm step.

        The returned token is a Django password reset token that can be
        consumed by ``reset_password``.
        """
        normalized_email = email.strip().lower()

        record = (
            PasswordResetOtp.objects.filter(
                email=normalized_email,
                is_used=False,
            )
            .select_related("user")
            .order_by("-created_at")
            .first()
        )

        if not record:
            raise ValueError("Invalid OTP. Please request a new code.")

        if record.is_expired:
            raise ValueError("This OTP has expired. Please request a new code.")

        if record.attempts >= cls.OTP_MAX_ATTEMPTS:
            raise ValueError(
                "Too many failed attempts. Please request a new code."
            )

        if not secrets.compare_digest(
            record.otp_hash,
            cls._hash_otp(otp.strip()),
        ):
            record.attempts += 1
            record.save(update_fields=["attempts", "updated_at"])
            raise ValueError(
                "Invalid OTP. Please check the code and try again."
            )

        record.is_used = True
        record.save(update_fields=["is_used", "updated_at"])

        uid = urlsafe_base64_encode(force_bytes(record.user.pk))
        token = cls._token_generator.make_token(record.user)
        return uid, token

    @classmethod
    def request_password_reset(cls, email: str) -> None:
        """
        Generate and send a password reset email.

        Never reveals whether the email exists.
        """
        user = (
            User.objects.filter(email__iexact=email, is_active=True)
            .only("id", "email")
            .first()
        )

        if not user:
            return

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = cls._token_generator.make_token(user)

        reset_url = (
            f"{settings.FRONTEND_URL}"
            f"/reset-password"
            f"?uid={uid}&token={token}"
        )

        context = {
            "user": user,
            "reset_url": reset_url,
        }

        subject = "Reset Your Password"

        message = render_to_string(
            "emails/password_reset.txt",
            context,
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email], # type: ignore
            fail_silently=False,
        )

    @classmethod
    @transaction.atomic
    def reset_password(
        cls,
        uid: str,
        token: str,
        new_password: str,
    ) -> None:
        """
        Validate reset token and update the user's password.
        """
        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id, is_active=True)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as exc:
            raise ValueError("Invalid password reset link.") from exc

        if not cls._token_generator.check_token(user, token):
            raise ValueError("Password reset link is invalid or has expired.")

        user.set_password(new_password)
        user.save(
            update_fields=[
                "password",
                "password_changed_at",
                "password_version",
            ]
        )

        from authentication.services.session_service import SessionService

        SessionService.revoke_all_sessions(user=user)
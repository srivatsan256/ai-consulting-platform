"""
Email verification service.

Handles generating verification tokens
and verifying user email addresses.
"""

from __future__ import annotations

from typing import Final

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)


User = get_user_model()


class EmailVerificationService:
    """
    Service responsible for email verification operations.
    """

    _token_generator: Final = PasswordResetTokenGenerator()


    @classmethod
    def send_verification_email(
        cls,
        email: str,
    ) -> None:
        """
        Generate and send email verification link.
        """

        user = (
            User.objects.filter(
                email__iexact=email,
                is_active=True,
            )
            .only(
                "id",
                "email",
                "is_email_verified",
            )
            .first()
        )

        if not user:
            return

        if user.is_email_verified: # type: ignore
            return

        uid = urlsafe_base64_encode(
            force_bytes(user.pk)
        )

        token = cls._token_generator.make_token(
            user
        )

        verification_url = (
            f"{settings.FRONTEND_URL}"
            f"/verify-email"
            f"?uid={uid}&token={token}"
        )

        context = {
            "user": user,
            "verification_url": verification_url,
        }

        message = render_to_string(
            "emails/email_verification.txt",
            context,
        )

        send_mail(
            subject="Verify Your Email Address",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[
                user.email, # type: ignore
            ],
            fail_silently=False,
        )


    @classmethod
    @transaction.atomic
    def verify_email(
        cls,
        uid: str,
        token: str,
    ) -> None:
        """
        Verify user email using token.
        """

        try:
            user_id = urlsafe_base64_decode(
                uid
            ).decode()

            user = User.objects.get(
                pk=user_id,
                is_active=True,
            )

        except Exception as exc:
            raise ValueError(
                "Invalid verification link."
            ) from exc


        if not cls._token_generator.check_token(
            user,
            token,
        ):
            raise ValueError(
                "Verification link is invalid or expired."
            )


        if not user.is_email_verified: # type: ignore

            user.is_email_verified = True # type: ignore

            user.save(
                update_fields=[
                    "is_email_verified",
                ]
            )
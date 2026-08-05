from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class PasswordResetOtp(models.Model):
    """
    Stores hashed one-time passwords for the password reset flow.

    One record represents a single issued OTP for a user's email.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_otps",
    )

    email = models.EmailField(
        max_length=254,
        db_index=True,
        help_text="Normalized email the OTP was issued to.",
    )

    otp_hash = models.CharField(
        max_length=64,
        help_text="SHA-256 hash of the 6-digit OTP.",
    )

    expires_at = models.DateTimeField(
        help_text="OTP is no longer valid after this timestamp.",
    )

    is_used = models.BooleanField(
        default=False,
        help_text="Marked True once the OTP has been successfully verified.",
    )

    attempts = models.PositiveSmallIntegerField(
        default=0,
        help_text="Number of failed verification attempts against this OTP.",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "authentication_password_reset_otp"
        verbose_name = "Password Reset OTP"
        verbose_name_plural = "Password Reset OTPs"
        ordering = ("-created_at",)

        indexes = [
            models.Index(fields=["email", "is_used"]),
            models.Index(fields=["email", "expires_at"]),
        ]

    def __str__(self) -> str:
        return f"OTP for {self.email} (expires {self.expires_at})"

    @property
    def is_expired(self) -> bool:
        """
        Return whether the OTP has expired.
        """
        return timezone.now() > self.expires_at

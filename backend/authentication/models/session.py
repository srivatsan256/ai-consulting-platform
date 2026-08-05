from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from companies.models import Company


class UserSessionQuerySet(models.QuerySet):
    """
    Custom queryset for user sessions.
    """

    def active(self) -> "UserSessionQuerySet":
        """Return active, non-expired sessions."""
        return self.filter(
            is_active=True,
            expires_at__gt=timezone.now(),
        )

    def expired(self) -> "UserSessionQuerySet":
        """Return expired sessions."""
        return self.filter(
            expires_at__lte=timezone.now(),
        )


class UserSessionManager(models.Manager):
    """
    Manager for UserSession.
    """

    def get_queryset(self) -> UserSessionQuerySet:
        return UserSessionQuerySet(self.model, using=self._db)

    def active(self) -> UserSessionQuerySet:
        return self.get_queryset().active()

    def expired(self) -> UserSessionQuerySet:
        return self.get_queryset().expired()


class UserSession(models.Model):
    """
    Stores every authenticated user session.

    One record represents one refresh token / one logged-in device.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="user_sessions",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_sessions",
    )

    refresh_token_jti = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="JWT Refresh Token JTI",
    )

    device_name = models.CharField(
        max_length=255,
        blank=True,
    )

    device_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="Desktop, Mobile, Tablet, API, etc.",
    )

    browser = models.CharField(
        max_length=150,
        blank=True,
    )

    operating_system = models.CharField(
        max_length=150,
        blank=True,
    )

    ip_address = models.GenericIPAddressField()

    user_agent = models.TextField()

    login_at = models.DateTimeField(
        auto_now_add=True,
    )

    last_activity_at = models.DateTimeField(
        default=timezone.now,
    )

    expires_at = models.DateTimeField()

    is_active = models.BooleanField(
        default=True,
    )

    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    objects = UserSessionManager()

    class Meta:
        db_table = "authentication_user_session"
        verbose_name = "User Session"
        verbose_name_plural = "User Sessions"
        ordering = ("-last_activity_at",)

        indexes = [
            models.Index(fields=["company", "user"]),
            models.Index(fields=["company", "is_active"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["last_activity_at"]),
            models.Index(fields=["refresh_token_jti"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} ({self.device_name or self.browser or 'Unknown Device'})"

    @property
    def is_expired(self) -> bool:
        """
        Return whether the session has expired.
        """
        return timezone.now() >= self.expires_at

    @property
    def is_valid(self) -> bool:
        """
        Return whether the session is currently valid.
        """
        return self.is_active and not self.is_expired

    def mark_activity(self) -> None:
        """
        Update last activity timestamp.
        """
        self.last_activity_at = timezone.now()
        self.save(update_fields=["last_activity_at", "updated_at"])

    def revoke(self) -> None:
        """
        Revoke this session.
        """
        self.is_active = False
        self.revoked_at = timezone.now()
        self.save(
            update_fields=[
                "is_active",
                "revoked_at",
                "updated_at",
            ]
        )
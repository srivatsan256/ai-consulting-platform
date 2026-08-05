"""
Login History Model.

Stores all authentication events for auditing purposes.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models

from companies.models import Company


class LoginHistory(models.Model):
    """
    Stores authentication events.

    Every login, failed login and logout generates one record.
    """

    class EventType(models.TextChoices):
        LOGIN_SUCCESS = "LOGIN_SUCCESS", "Login Success"
        LOGIN_FAILED = "LOGIN_FAILED", "Login Failed"
        LOGOUT = "LOGOUT", "Logout"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="login_history",
        null=True,
        blank=True,
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        related_name="login_history",
        null=True,
        blank=True,
    )

    event_type = models.CharField(
        max_length=30,
        choices=EventType.choices,
        db_index=True,
    )

    email = models.EmailField(
        max_length=254,
        blank=True,
        help_text=(
            "Email address associated with the authentication event. "
            "Captured for failed login attempts where no user can be resolved."
        ),
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    user_agent = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["event_type"]),
        ]
        verbose_name = "Login History"
        verbose_name_plural = "Login History"

    def __str__(self) -> str:
        user = self.user.email if self.user else "Unknown User"
        return f"{user} - {self.event_type} ({self.created_at:%Y-%m-%d %H:%M:%S})"
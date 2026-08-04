from django.db import models

from accounts.models import User
from companies.models import Company


class AuditLog(models.Model):

    ACTION = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("login", "Login"),
        ("failed_login", "Failed Login"),
        ("logout", "Logout"),
        ("approve", "Approve"),
        ("reject", "Reject"),
        ("export", "Export"),
        ("password_change", "Password Change"),
        ("session_created", "Session Created"),
        ("session_revoked", "Session Revoked"),
        ("sessions_revoked", "Sessions Revoked"),
        ("soft_delete", "Soft Delete"),
        ("permission_change", "Permission Change"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
    )

    action = models.CharField(
        max_length=30,
        choices=ACTION,
    )

    entity_type = models.CharField(max_length=100)

    entity_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    entity_name = models.CharField(
        max_length=255,
        blank=True,
    )

    changes = models.JSONField(
        default=dict,
        blank=True,
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    user_agent = models.TextField(blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.entity_type}"

from django.db import models

from accounts.models import User
from projects.models import Project


class Deployment(models.Model):

    STATUS = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("rolled_back", "Rolled Back"),
    ]

    ENVIRONMENT = [
        ("development", "Development"),
        ("staging", "Staging"),
        ("production", "Production"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="deployments",
    )

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    version = models.CharField(max_length=50)

    environment = models.CharField(
        max_length=20,
        choices=ENVIRONMENT,
        default="development",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending",
    )

    deployed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="deployments_performed",
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deployments_approved",
    )

    changelog = models.TextField(blank=True)

    rollback_notes = models.TextField(blank=True)

    deployed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "deployments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} v{self.version}"

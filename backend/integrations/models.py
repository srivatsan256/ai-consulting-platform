from django.db import models

from accounts.models import User
from projects.models import Project


class Integration(models.Model):

    STATUS = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("error", "Error"),
    ]

    INTEGRATION_TYPE = [
        ("slack", "Slack"),
        ("jira", "Jira"),
        ("github", "GitHub"),
        ("gitlab", "GitLab"),
        ("confluence", "Confluence"),
        ("salesforce", "Salesforce"),
        ("azure", "Azure DevOps"),
        ("custom", "Custom"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="integrations",
    )

    name = models.CharField(max_length=255)

    integration_type = models.CharField(
        max_length=20,
        choices=INTEGRATION_TYPE,
        default="custom",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="inactive",
    )

    api_key = models.CharField(
        max_length=500,
        blank=True,
    )

    api_url = models.URLField(blank=True)

    config = models.JSONField(
        default=dict,
        blank=True,
    )

    last_sync_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    error_message = models.TextField(blank=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="integrations_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "integrations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_integration_type_display()})"

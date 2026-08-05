from django.db import models

from accounts.models import User
from projects.models import Project


class Report(models.Model):

    REPORT_TYPE = [
        ("status", "Status Report"),
        ("progress", "Progress Report"),
        ("financial", "Financial Report"),
        ("risk", "Risk Report"),
        ("resource", "Resource Report"),
        ("executive", "Executive Summary"),
        ("technical", "Technical Report"),
    ]

    STATUS = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="reports",
    )

    title = models.CharField(max_length=255)

    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE,
        default="status",
    )

    content = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="draft",
    )

    file = models.FileField(
        upload_to="reports/",
        blank=True,
        null=True,
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reports_created",
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reports"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

from django.db import models

from accounts.models import User
from projects.models import Project


class DocumentTemplate(models.Model):

    CATEGORY = [
        ("proposal", "Proposal"),
        ("sow", "Statement of Work"),
        ("report", "Report"),
        ("contract", "Contract"),
        ("presentation", "Presentation"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY,
        default="other",
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="document_templates",
    )

    file = models.FileField(
        upload_to="document_templates/",
    )

    original_filename = models.CharField(max_length=255)

    file_size = models.BigIntegerField(default=0)

    version = models.PositiveIntegerField(default=1)

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="templates_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "document_templates"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

from django.db import models

from projects.models import Project
from accounts.models import User


class Document(models.Model):

    DOCUMENT_TYPES = [
        ("vision", "Vision Document"),
        ("business_case", "Business Case"),
        ("brd", "Business Requirements Document"),
        ("frd", "Functional Requirements Document"),
        ("prd", "Product Requirements Document"),
        ("nfr", "Non Functional Requirements"),
        ("user_story", "User Story"),
        ("use_case", "Use Case"),
        ("process_flow", "Process Flow"),
        ("architecture", "Architecture"),
        ("security", "Security"),
        ("test_plan", "Test Plan"),
        ("deployment", "Deployment"),
        ("uat", "User Acceptance Testing"),
        ("signoff", "Sign Off"),
    ]

    STATUS = [
        ("draft", "Draft"),
        ("review", "Under Review"),
        ("approved", "Approved"),
        ("published", "Published"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPES
    )

    title = models.CharField(
        max_length=255
    )

    content = models.TextField(blank=True)

    version = models.PositiveIntegerField(default=1)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="draft"
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="documents_created"
    )

    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="documents_updated"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        db_table = "documents"
        ordering = ["document_type", "-version"]

    def __str__(self):
        return self.title

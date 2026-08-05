from django.db import models
from django.core.exceptions import ValidationError

from projects.models import Project
from accounts.models import User


class Discovery(models.Model):

    INPUT_TYPE = [
        ("text", "Text"),
        ("pdf", "PDF"),
    ]

    STATUS = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("needs_info", "Needs More Info"),
        ("review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="discoveries",
        null=True,
        blank=True,
    )

    input_type = models.CharField(
        max_length=10,
        choices=INPUT_TYPE,
        default="text"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="draft"
    )

    version = models.PositiveIntegerField(default=1)

    completeness_score = models.PositiveIntegerField(
        default=0,
        help_text="Auto-calculated completeness percentage 0-100",
    )

    ai_processed = models.BooleanField(
        default=False,
        help_text="Whether AI has processed this discovery",
    )

    remarks = models.TextField(blank=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="discoveries_created"
    )

    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="discoveries_updated"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "discoveries"
        ordering = ["-created_at"]

    def __str__(self):
        return self.project.project_name


class DiscoveryText(models.Model):

    discovery = models.OneToOneField(
        Discovery,
        on_delete=models.CASCADE,
        related_name="text_content"
    )

    executive_summary = models.TextField(blank=True)

    business_problem = models.TextField()

    business_goal = models.TextField()

    current_process = models.TextField()

    future_process = models.TextField(blank=True)

    stakeholders = models.TextField(blank=True)

    departments = models.TextField(blank=True)

    users = models.TextField(blank=True)

    assumptions = models.TextField(blank=True)

    constraints = models.TextField(blank=True)

    pain_points = models.TextField()

    opportunities = models.TextField(blank=True)

    functional_requirements = models.TextField(blank=True)

    non_functional_requirements = models.TextField(blank=True)

    risks = models.TextField(blank=True)

    dependencies = models.TextField(blank=True)

    success_criteria = models.TextField(blank=True)

    expected_roi = models.TextField(blank=True)

    additional_notes = models.TextField(blank=True)

    class Meta:
        db_table = "discovery_text"

    def clean(self):
        if self.discovery.input_type != "text":
            raise ValidationError(
                "This discovery is configured for PDF input."
            )

    def __str__(self):
        return f"{self.discovery.project.project_name} - Text"


class DiscoveryDocument(models.Model):

    discovery = models.OneToOneField(
        Discovery,
        on_delete=models.CASCADE,
        related_name="document"
    )

    uploaded_file = models.FileField(
        upload_to="discovery/"
    )

    original_filename = models.CharField(
        max_length=255
    )

    file_size = models.BigIntegerField()

    extracted_text = models.TextField(
        blank=True
    )

    ai_summary = models.TextField(
        blank=True
    )

    total_pages = models.PositiveIntegerField(
        default=0
    )

    upload_time = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "discovery_documents"

    def clean(self):
        if self.discovery.input_type != "pdf":
            raise ValidationError(
                "This discovery is configured for Text input."
            )

    def __str__(self):
        return self.original_filename
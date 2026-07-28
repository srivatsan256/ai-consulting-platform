import uuid
from django.db import models  # type: ignore


class Project(models.Model):
    STATUS_CHOICES = [
        ("DISCOVERY", "Discovery Phase"),
        ("VERIFICATION", "Sequential Verification"),
        ("PROCESSING", "AI Processing"),
        ("REVIEW", "Final Review & Delivery"),
        ("COMPLETED", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    company_name = models.CharField(max_length=200)
    industry = models.CharField(max_length=100, blank=True)
    project_name = models.CharField(max_length=200)
    objectives = models.TextField(blank=True)
    
    team_members = models.TextField(
        help_text="Comma-separated team member names or JSON list"
    )
    expected_timeline = models.CharField(max_length=100, blank=True)
    completed_levels = models.JSONField(default=list, blank=True)
    current_level = models.IntegerField(default=0)
    level_scores = models.JSONField(default=list, blank=True)

    # AI Discovery Fields
    readiness_score = models.FloatField(null=True, blank=True)
    ai_validation_notes = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DISCOVERY",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return f"{self.project_name} ({self.company_name})"


class Document(models.Model):
    DOC_TYPES = [
        ("BRD", "Business Requirements Document"),
        ("FRD", "Functional Requirements Document"),
        ("PRD", "Product Requirements Document"),
        ("SOP", "Standard Operating Procedure"),
        ("OTHER", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=10, choices=DOC_TYPES)
    level = models.IntegerField(default=0)
    file = models.FileField(upload_to='uploads/documents/%Y/%m/%d/')
    extracted_text = models.TextField(blank=True)
    verification_status = models.BooleanField(default=False)
    missing_keywords = models.JSONField(default=list)
    missing_sections = models.JSONField(default=list)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.get_doc_type_display()} - {self.project.project_name}"


class VerificationReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='verification_report')
    report_data = models.JSONField()
    summary = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.project.project_name}"
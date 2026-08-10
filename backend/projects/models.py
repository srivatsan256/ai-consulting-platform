from django.db import models
from companies.models import Company
from accounts.models import User


class Project(models.Model):

    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("discovery", "Discovery"),
        ("development", "Development"),
        ("testing", "Testing"),
        ("deployment", "Deployment"),
        ("completed", "Completed"),
        ("on_hold", "On Hold"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    project_name = models.CharField(max_length=255)

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="projects"
    )

    project_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="managed_projects"
    )

    description = models.TextField(blank=True)

    industry = models.CharField(
        max_length=150,
        blank=True,
        help_text="Project industry",
    )

    team_members = models.TextField(
        blank=True,
        help_text="Comma-separated team member names",
    )

    objectives = models.TextField(
        blank=True,
        help_text="Project objectives extracted from discovery",
    )

    expected_timeline = models.CharField(
        max_length=255,
        blank=True,
        help_text="Expected project duration or timeline",
    )

    start_date = models.DateField()

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="planning"
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="medium"
    )

    progress = models.PositiveIntegerField(default=0)

    # Level-based verification state (used by the consulting frontend)
    current_level = models.PositiveIntegerField(default=1)

    completed_levels = models.JSONField(
        default=list,
        blank=True,
        help_text="Levels that have passed verification",
    )

    level_scores = models.JSONField(
        default=dict,
        blank=True,
        help_text="Readiness score per level",
    )

    readiness_score = models.PositiveIntegerField(default=0)

    verification_report = models.JSONField(
        null=True,
        blank=True,
        help_text="Latest verification report",
    )

    is_active = models.BooleanField(default=True)

    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="List of tag strings for categorizing the project",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projects"
        ordering = ["project_name"]

    def __str__(self):
        return self.project_name


class ProjectPhase(models.Model):

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="phases"
    )

    phase_name = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=1)

    completed = models.BooleanField(default=False)

    class Meta:
        db_table = "project_phases"
        ordering = ["order"]

    def __str__(self):
        return f"{self.project.project_name} - {self.phase_name}"


class Milestone(models.Model):

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="milestones"
    )

    title = models.CharField(max_length=200)

    due_date = models.DateField()

    completed = models.BooleanField(default=False)

    class Meta:
        db_table = "milestones"

    def __str__(self):
        return self.title


class LevelModule(models.Model):
    """
    Conditions that must be satisfied to pass a given level.
    """

    level = models.PositiveIntegerField(unique=True)

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    icon = models.CharField(max_length=50, default="layers")

    must_include = models.JSONField(
        default=list,
        blank=True,
        help_text="List of {id, text} required items",
    )

    recommended = models.JSONField(
        default=list,
        blank=True,
        help_text="List of {id, text} recommended items",
    )

    required_documents = models.JSONField(
        default=list,
        blank=True,
        help_text="List of {id, label} required document types",
    )

    required_count = models.PositiveIntegerField(default=3)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "level_modules"
        ordering = ["level"]

    def __str__(self):
        return f"Level {self.level} - {self.title}"


class ProjectDocument(models.Model):
    """
    Uploaded source file attached to a project at a given level.
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="uploaded_documents"
    )

    file = models.FileField(upload_to="project_documents/")

    file_size = models.PositiveBigIntegerField(default=0)

    original_name = models.CharField(max_length=255, blank=True)

    doc_type = models.CharField(max_length=20, default="OTHER")

    file_category = models.ForeignKey(
        "file_management.FileCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="files",
    )

    level = models.PositiveIntegerField(default=1)

    extracted_text = models.TextField(blank=True)

    verification_status = models.BooleanField(default=False)

    verification_score = models.PositiveIntegerField(default=0)

    missing_requirements = models.JSONField(
        default=list,
        blank=True,
        help_text="Required items missing from the document",
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_documents_uploaded"
    )

    class Meta:
        db_table = "project_documents"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.original_name or self.file.name} @ {self.project.project_name}"

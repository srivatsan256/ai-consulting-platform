from django.db import models

from accounts.models import User
from projects.models import Project


class AIAssessment(models.Model):

    STATUS = [
        ("draft", "Draft"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    MATURITY_LEVEL = [
        (1, "Level 1 - Initial"),
        (2, "Level 2 - Managed"),
        (3, "Level 3 - Defined"),
        (4, "Level 4 - Quantitatively Managed"),
        (5, "Level 5 - Optimizing"),
    ]

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name="ai_assessment",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="draft",
    )

    overall_score = models.PositiveIntegerField(
        choices=MATURITY_LEVEL,
        null=True,
        blank=True,
    )

    data_readiness_score = models.PositiveIntegerField(
        choices=MATURITY_LEVEL,
        null=True,
        blank=True,
    )

    infrastructure_score = models.PositiveIntegerField(
        choices=MATURITY_LEVEL,
        null=True,
        blank=True,
    )

    talent_score = models.PositiveIntegerField(
        choices=MATURITY_LEVEL,
        null=True,
        blank=True,
    )

    strategy_score = models.PositiveIntegerField(
        choices=MATURITY_LEVEL,
        null=True,
        blank=True,
    )

    executive_summary = models.TextField(blank=True)

    recommendations = models.TextField(blank=True)

    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="ai_assessments_completed",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="ai_assessments_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_assessments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"AI Assessment - {self.project.project_name}"


class AIUseCase(models.Model):

    PRIORITY = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    STATUS = [
        ("identified", "Identified"),
        ("evaluated", "Evaluated"),
        ("approved", "Approved"),
        ("in_development", "In Development"),
        ("deployed", "Deployed"),
    ]

    assessment = models.ForeignKey(
        AIAssessment,
        on_delete=models.CASCADE,
        related_name="use_cases",
    )

    title = models.CharField(max_length=255)

    description = models.TextField()

    business_value = models.TextField(blank=True)

    technical_feasibility = models.TextField(blank=True)

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY,
        default="medium",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="identified",
    )

    estimated_roi = models.CharField(max_length=255, blank=True)

    estimated_timeline = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_use_cases"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

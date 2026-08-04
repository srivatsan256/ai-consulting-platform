from django.db import models

from accounts.models import User
from projects.models import Project


class ArchitectureDiagram(models.Model):

    CATEGORY = [
        ("system", "System Architecture"),
        ("data", "Data Architecture"),
        ("network", "Network Architecture"),
        ("cloud", "Cloud Architecture"),
        ("integration", "Integration Architecture"),
        ("security", "Security Architecture"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="architecture_diagrams",
    )

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY,
        default="system",
    )

    file = models.FileField(
        upload_to="architecture/",
        blank=True,
        null=True,
    )

    diagram_url = models.URLField(blank=True)

    version = models.PositiveIntegerField(default=1)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="architecture_diagrams_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "architecture_diagrams"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class TechnologyStack(models.Model):

    CATEGORY = [
        ("frontend", "Frontend"),
        ("backend", "Backend"),
        ("database", "Database"),
        ("devops", "DevOps"),
        ("ai_ml", "AI/ML"),
        ("infrastructure", "Infrastructure"),
        ("other", "Other"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="technology_stacks",
    )

    name = models.CharField(max_length=255)

    version = models.CharField(max_length=50, blank=True)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY,
        default="other",
    )

    purpose = models.TextField(blank=True)

    license_type = models.CharField(max_length=100, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "technology_stacks"
        ordering = ["category", "name"]

    def __str__(self):
        return self.name

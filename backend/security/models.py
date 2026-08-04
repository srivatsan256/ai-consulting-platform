from django.db import models

from accounts.models import User
from projects.models import Project


class SecurityChecklist(models.Model):

    STATUS = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("passed", "Passed"),
        ("failed", "Failed"),
        ("not_applicable", "Not Applicable"),
    ]

    CATEGORY = [
        ("authentication", "Authentication"),
        ("authorization", "Authorization"),
        ("encryption", "Encryption"),
        ("network", "Network Security"),
        ("data_protection", "Data Protection"),
        ("compliance", "Compliance"),
        ("vulnerability", "Vulnerability Assessment"),
        ("incident_response", "Incident Response"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="security_checklists",
    )

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY,
        default="authentication",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending",
    )

    notes = models.TextField(blank=True)

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="security_tasks",
    )

    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="security_verifications",
    )

    due_date = models.DateField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "security_checklists"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class VulnerabilityReport(models.Model):

    SEVERITY = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    STATUS = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("mitigated", "Mitigated"),
        ("resolved", "Resolved"),
        ("accepted", "Accepted"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="vulnerability_reports",
    )

    title = models.CharField(max_length=255)

    description = models.TextField()

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY,
        default="medium",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="open",
    )

    affected_component = models.CharField(max_length=255, blank=True)

    mitigation = models.TextField(blank=True)

    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="vulnerabilities_reported",
    )

    reported_date = models.DateField(auto_now_add=True)

    resolved_date = models.DateField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vulnerability_reports"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

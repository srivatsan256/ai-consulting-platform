from django.db import models

from accounts.models import User
from projects.models import Project


class Risk(models.Model):

    STATUS = [
        ("open", "Open"),
        ("mitigated", "Mitigated"),
        ("closed", "Closed"),
        ("accepted", "Accepted"),
    ]

    SEVERITY = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    PROBABILITY = [
        ("unlikely", "Unlikely"),
        ("possible", "Possible"),
        ("likely", "Likely"),
        ("almost_certain", "Almost Certain"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="risks",
    )

    title = models.CharField(max_length=255)

    description = models.TextField()

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY,
        default="medium",
    )

    probability = models.CharField(
        max_length=20,
        choices=PROBABILITY,
        default="possible",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="open",
    )

    mitigation_plan = models.TextField(blank=True)

    impact = models.TextField(blank=True)

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="owned_risks",
    )

    identified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="risks_identified",
    )

    identified_date = models.DateField(auto_now_add=True)

    target_resolution_date = models.DateField(
        null=True,
        blank=True,
    )

    resolved_date = models.DateField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "risks"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

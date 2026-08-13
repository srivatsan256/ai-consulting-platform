from django.db import models
from django.utils import timezone


class Priority(models.TextChoices):
    HIGH = "High", "High"
    MEDIUM = "Medium", "Medium"
    LOW = "Low", "Low"


class Feasibility(models.TextChoices):
    HIGH = "High", "High"
    MEDIUM = "Medium", "Medium"
    LOW = "Low", "Low"


class Status(models.TextChoices):
    OPEN = "Open", "Open"
    IN_PROGRESS = "In Progress", "In Progress"
    COMPLETED = "Completed", "Completed"
    ON_HOLD = "On Hold", "On Hold"
    CANCELLED = "Cancelled", "Cancelled"


class AIInterventionPainArea(models.Model):
    date = models.DateField(default=timezone.localdate)
    department = models.CharField(max_length=255, blank=True, default="")
    process_activity = models.CharField(max_length=255, blank=True, default="")
    pain_area = models.TextField(blank=True, default="")
    current_method = models.TextField(blank=True, default="")
    frequency = models.CharField(max_length=100, blank=True, default="")
    time_spent_hrs = models.FloatField(null=True, blank=True)
    impact_area = models.CharField(max_length=255, blank=True, default="")
    ai_intervention = models.TextField(blank=True, default="")
    expected_benefit = models.TextField(blank=True, default="")
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    feasibility = models.CharField(
        max_length=20,
        choices=Feasibility.choices,
        default=Feasibility.MEDIUM,
    )
    owner = models.CharField(max_length=255, blank=True, default="")
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    remarks = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_intervention_pain_areas_tracker"
        managed = False
        ordering = ["-date", "-created_at"]
        verbose_name = "AI Intervention Pain Area"
        verbose_name_plural = "AI Intervention Pain Areas"

    def __str__(self):
        return f"{self.process_activity} ({self.status})"

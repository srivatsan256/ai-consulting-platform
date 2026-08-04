from django.db import models

from accounts.models import User
from projects.models import Project


class MonitoringAlert(models.Model):

    SEVERITY = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("critical", "Critical"),
    ]

    STATUS = [
        ("active", "Active"),
        ("acknowledged", "Acknowledged"),
        ("resolved", "Resolved"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="monitoring_alerts",
    )

    title = models.CharField(max_length=255)

    message = models.TextField()

    severity = models.CharField(
        max_length=20,
        choices=SEVERITY,
        default="info",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="active",
    )

    source = models.CharField(max_length=255, blank=True)

    metric_name = models.CharField(max_length=255, blank=True)

    metric_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alerts_acknowledged",
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "monitoring_alerts"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class SystemMetric(models.Model):

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="system_metrics",
    )

    metric_name = models.CharField(max_length=255)

    metric_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    unit = models.CharField(max_length=50, blank=True)

    source = models.CharField(max_length=255, blank=True)

    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "system_metrics"
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.metric_name}: {self.metric_value}"

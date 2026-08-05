from django.db import models

from accounts.models import User
from projects.models import Project


class DashboardWidget(models.Model):

    WIDGET_TYPE = [
        ("project_summary", "Project Summary"),
        ("task_overview", "Task Overview"),
        ("risk_matrix", "Risk Matrix"),
        ("timeline", "Timeline"),
        ("chart", "Chart"),
        ("recent_activity", "Recent Activity"),
        ("team_performance", "Team Performance"),
    ]

    title = models.CharField(max_length=255)

    widget_type = models.CharField(
        max_length=20,
        choices=WIDGET_TYPE,
    )

    config = models.JSONField(
        default=dict,
        blank=True,
    )

    position = models.PositiveIntegerField(default=0)

    is_visible = models.BooleanField(default=True)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="dashboard_widgets",
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="dashboard_widgets",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "dashboard_widgets"
        ordering = ["position"]

    def __str__(self):
        return self.title

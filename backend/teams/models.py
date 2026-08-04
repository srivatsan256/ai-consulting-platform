from django.db import models

from departments.models import Department


class Team(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="teams",
    )

    team_name = models.CharField(max_length=150)

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "teams"
        unique_together = ("department", "team_name")
        ordering = ["team_name"]

    def __str__(self):
        return self.team_name

from django.db import models

from accounts.models import User
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


class TeamMember(models.Model):
    ROLE = [
        ("member", "Member"),
        ("lead", "Lead"),
        ("manager", "Manager"),
    ]

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="members",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="team_memberships",
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE,
        default="member",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "team_members"
        unique_together = ("team", "user")
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user} in {self.team}"

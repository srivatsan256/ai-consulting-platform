from django.db import models

from projects.models import Project
from accounts.models import User
from roles.models import Role


class ProjectMember(models.Model):

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="members"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="project_memberships"
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "project_members"
        unique_together = ("project", "user")

    def __str__(self):
        return f"{self.project.project_name} - {self.user.email}"
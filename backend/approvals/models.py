from django.db import models

from accounts.models import User
from projects.models import Project


class Approval(models.Model):

    STATUS = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]

    ENTITY_TYPE = [
        ("discovery", "Discovery"),
        ("document", "Document"),
        ("workflow", "Workflow"),
        ("task", "Task"),
        ("risk", "Risk"),
        ("issue", "Issue"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="approvals",
    )

    entity_type = models.CharField(
        max_length=20,
        choices=ENTITY_TYPE,
    )

    entity_id = models.PositiveIntegerField()

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending",
    )

    requested_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="approvals_requested",
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="approvals_assigned",
    )

    decision_date = models.DateTimeField(
        null=True,
        blank=True,
    )

    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "approvals"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.status}"

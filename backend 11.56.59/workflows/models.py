from django.db import models

from accounts.models import User
from projects.models import Project


class Workflow(models.Model):

    STATUS = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="workflows",
    )

    name = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="draft",
    )

    trigger_event = models.CharField(max_length=100)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="workflows_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "workflows"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class WorkflowStep(models.Model):

    STEP_TYPE = [
        ("approval", "Approval"),
        ("notification", "Notification"),
        ("task", "Task"),
        ("condition", "Condition"),
        ("wait", "Wait"),
    ]

    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name="steps",
    )

    name = models.CharField(max_length=255)

    step_type = models.CharField(
        max_length=20,
        choices=STEP_TYPE,
    )

    order = models.PositiveIntegerField(default=1)

    assignee_role = models.CharField(max_length=100, blank=True)

    config = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        db_table = "workflow_steps"
        ordering = ["order"]

    def __str__(self):
        return f"{self.workflow.name} - {self.name}"


class WorkflowExecution(models.Model):

    STATUS = [
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name="executions",
    )

    entity_type = models.CharField(max_length=100)

    entity_id = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="running",
    )

    current_step = models.ForeignKey(
        WorkflowStep,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="executions",
    )

    initiated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="workflow_executions",
    )

    started_at = models.DateTimeField(auto_now_add=True)

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "workflow_executions"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.workflow.name} - {self.status}"

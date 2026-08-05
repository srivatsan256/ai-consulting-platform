from django.db import models

from accounts.models import User
from projects.models import Project


class Issue(models.Model):

    STATUS = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
        ("reopened", "Reopened"),
    ]

    PRIORITY = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    CATEGORY = [
        ("bug", "Bug"),
        ("feature", "Feature Request"),
        ("improvement", "Improvement"),
        ("task", "Task"),
        ("epic", "Epic"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="issues",
    )

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="open",
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY,
        default="medium",
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY,
        default="bug",
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_issues",
    )

    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reported_issues",
    )

    resolution_notes = models.TextField(blank=True)

    due_date = models.DateField(
        null=True,
        blank=True,
    )

    resolved_date = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "issues"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class IssueComment(models.Model):

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="issue_comments",
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "issue_comments"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.issue}"

from django.db import models
from roles.models import Role


class Permission(models.Model):
    FEATURE_CHOICES = [
        ("dashboard", "Dashboard"),
        ("company_management", "Company Management"),
        ("user_management", "User Management"),
        ("role_management", "Role Management"),
        ("project_management", "Project Management"),
        ("discovery", "Discovery"),
        ("document_management", "Document Management"),
        ("review_management", "Review Management"),
        ("approval_management", "Approval Management"),
        ("ai_chat", "AI Chat"),
        ("knowledge_base", "Knowledge Base"),
        ("reports", "Reports"),
        ("audit_logs", "Audit Logs"),
        ("settings", "Settings"),
        ("login_history", "Login History"),
    ]

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="permissions"
    )

    feature = models.CharField(
        max_length=50,
        choices=FEATURE_CHOICES
    )

    can_view = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_review = models.BooleanField(default=False)
    can_approve = models.BooleanField(default=False)
    can_export = models.BooleanField(default=False)

    class Meta:
        db_table = "permissions"
        unique_together = ("role", "feature")
        ordering = ["feature"]

    def __str__(self):
        return f"{self.role.display_name} - {self.feature}"
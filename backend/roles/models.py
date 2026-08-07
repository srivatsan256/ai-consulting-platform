from django.db import models


class Role(models.Model):
    ROLE_CHOICES = [
        ("super_admin", "Super Admin"),
        ("company_admin", "Company Admin"),
        ("project_manager", "Project Manager"),
        ("business_analyst", "Business Analyst"),
        ("solution_architect", "Solution Architect"),
        ("ai_ml_engineer", "Artificial Intelligence/Machine Learning Engineer"),
        ("backend_developer", "Backend Developer"),
        ("frontend_developer", "Frontend Developer"),
        ("qa_test_engineer", "Quality Assurance/Test Engineer"),
        ("security_consultant", "Security Consultant"),
        ("devops_engineer", "DevOps Engineer"),
        ("document_reviewer", "Document Reviewer"),
    ]

    role_key = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "roles"
        ordering = ["display_name"]

    def __str__(self):
        return self.display_name


class RoleAssignment(models.Model):
    """
    Audit trail for user-role assignments within a company.

    The source of truth for a user's current role is ``CompanyMember.role``;
    this model records every assignment/change (who assigned which role to
    whom, from what previous role) for authorization auditing.
    """

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="role_assignments",
    )

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="role_assignments",
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="role_assignments",
        help_text="The role assigned to the user.",
    )

    previous_role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text="The role held before this assignment (null on first assignment).",
    )

    assigned_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text="The user who performed the assignment.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "role_assignments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} -> {self.role.role_key} @ {self.company.company_name}"
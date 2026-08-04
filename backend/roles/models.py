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
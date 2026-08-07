from django.db import models

from companies.models import Company
from accounts.models import User


class Department(models.Model):

    STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="detailed_departments",
    )

    name = models.CharField(
        max_length=150,
    )

    code = models.CharField(
        max_length=30,
    )

    description = models.TextField(
        blank=True,
    )

    head = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_departments",
    )

    email = models.EmailField(
        blank=True,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    location = models.CharField(
        max_length=200,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="departments_created",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = "department_details"
        ordering = ["company", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="unique_department_code_per_company",
            ),
            models.UniqueConstraint(
                fields=["company", "name"],
                name="unique_department_name_per_company",
            ),
        ]

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class DepartmentMember(models.Model):
    """
    Links a user to a department within a company.

    This is the source of truth for department-based access: a user is
    authorized to department-scoped data when an active ``DepartmentMember``
    row exists, or when they are the department ``head`` / a company admin.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="department_memberships",
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="members",
    )

    is_active = models.BooleanField(default=True)

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "department_members"
        unique_together = ("user", "department")
        ordering = ["department", "-joined_at"]

    def __str__(self):
        return f"{self.user.email} @ {self.department.name}"

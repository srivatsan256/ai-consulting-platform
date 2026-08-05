from django.db import models
from django.utils import timezone

from core.models import MembershipBaseModel
from .managers import MembershipManager


class CompanyMember(MembershipBaseModel):
    """
    Defines the relationship between User and Company.
    This is the source of truth for tenancy - NOT User.company.

    Permission chain:
    IsAuthenticated → IsCompanyMember → IsProjectMember → RolePermission
    """

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="company_memberships",
    )

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="members",
    )

    role = models.ForeignKey(
        "roles.Role",
        on_delete=models.PROTECT,
        related_name="company_memberships",
    )

    is_primary = models.BooleanField(
        default=False,
        help_text="Primary company for this user. Used for JWT claim.",
    )

    joined_at = models.DateTimeField(auto_now_add=True)

    last_accessed_at = models.DateTimeField(null=True, blank=True)

    objects = MembershipManager()

    class Meta:
        db_table = "company_members"
        unique_together = ("user", "company")
        ordering = ["-is_primary", "-joined_at"]

    def __str__(self):
        return f"{self.user.email} @ {self.company.company_name}"

    def mark_accessed(self):
        self.last_accessed_at = timezone.now()
        self.save(update_fields=["last_accessed_at"])

import secrets

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


class UserInvitation(models.Model):
    """
    Pending invite for a user to join a company.

    The invite token is shared via the invite link; the invitee completes
    onboarding by accepting the invitation (see the ``accept`` endpoint).
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("cancelled", "Cancelled"),
        ("expired", "Expired"),
    ]

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="invitations",
    )

    email = models.EmailField()

    role = models.ForeignKey(
        "roles.Role",
        on_delete=models.PROTECT,
        related_name="invitations",
    )

    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invitations",
    )

    invited_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    token = models.CharField(max_length=64, unique=True, editable=False)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    expires_at = models.DateTimeField()

    accepted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        db_table = "user_invitations"
        ordering = ["-created_at"]
        unique_together = ("company", "email", "status")

    def __str__(self):
        return f"Invite {self.email} -> {self.company.company_name} ({self.status})"

    def is_valid(self):
        return self.status == "pending" and self.expires_at > timezone.now()

    @classmethod
    def generate_token(cls):
        return secrets.token_urlsafe(32)

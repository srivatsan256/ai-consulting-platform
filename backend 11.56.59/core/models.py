from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract model for timestamp fields.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditModel(TimeStampedModel):
    """
    Tracks who created and updated records.
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_updated",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Soft delete support.
    """

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class MembershipBaseModel(TimeStampedModel):
    """
    Base for models that define tenant relationships (CompanyMember).
    Separate from CompanyBaseModel because membership resolves tenancy.
    """

    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class CompanyBaseModel(AuditModel, SoftDeleteModel):
    """
    Base model inherited by every tenant-aware model.
    Uses CompanyManager for tenant filtering.
    """

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="%(class)s_records",
    )

    class Meta:
        abstract = True

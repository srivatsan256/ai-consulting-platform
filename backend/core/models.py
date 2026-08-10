from django.conf import settings
from django.db import models
from django.utils import timezone


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


class SoftDeleteQuerySet(models.QuerySet):
    """
    QuerySet helpers for soft-deleted rows.
    """

    def alive(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)

    def soft_delete(self):
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def restore(self):
        return self.update(is_deleted=False, deleted_at=None)


class SoftDeleteManager(models.Manager):
    """
    Default manager that hides soft-deleted rows.
    """

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    def with_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted_only(self):
        return SoftDeleteQuerySet(self.model, using=self._db).deleted()


class SoftDeleteModel(models.Model):
    """
    Soft delete support with restore helpers.
    """

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        """
        Mark this row as deleted without removing it from the database.
        """
        if self.is_deleted:
            return self
        self.is_deleted = True
        self.deleted_at = timezone.now()
        update_fields = ["is_deleted", "deleted_at"]
        if hasattr(self, "updated_by_id") and user is not None:
            self.updated_by = user
            update_fields.append("updated_by")
        if hasattr(self, "updated_at"):
            update_fields.append("updated_at")
        self.save(update_fields=update_fields)
        try:
            from core.audit import record_soft_delete

            record_soft_delete(self, user=user)
        except Exception:  # noqa: BLE001 — audit must never block delete
            pass
        return self

    def restore(self, user=None):
        """
        Reverse a soft delete.
        """
        if not self.is_deleted:
            return self
        self.is_deleted = False
        self.deleted_at = None
        update_fields = ["is_deleted", "deleted_at"]
        if hasattr(self, "updated_by_id") and user is not None:
            self.updated_by = user
            update_fields.append("updated_by")
        if hasattr(self, "updated_at"):
            update_fields.append("updated_at")
        self.save(update_fields=update_fields)
        return self


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

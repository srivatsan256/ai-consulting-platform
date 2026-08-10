from django.db import models
from django.utils import timezone


class CompanyQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)

    def for_company(self, company):
        return self.active().filter(company=company)

    def soft_delete(self):
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def restore(self):
        return self.update(is_deleted=False, deleted_at=None)


class CompanyManager(models.Manager):
    """
    Manager for tenant-aware models (Project, Task, Risk, etc.).
    Assumes model has company FK and is_deleted field.

    Default queryset hides soft-deleted rows.
    """

    def get_queryset(self):
        return CompanyQuerySet(
            self.model,
            using=self._db,
        ).active()

    def active(self):
        return self.get_queryset()

    def deleted(self):
        return CompanyQuerySet(self.model, using=self._db).deleted()

    def with_deleted(self):
        return CompanyQuerySet(self.model, using=self._db)

    def for_company(self, company):
        return self.get_queryset().for_company(company)

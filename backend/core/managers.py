from django.db import models


class CompanyQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)

    def for_company(self, company):
        return self.active().filter(company=company)


class CompanyManager(models.Manager):
    """
    Manager for tenant-aware models (Project, Task, Risk, etc.).
    Assumes model has company FK and is_deleted field.
    """

    def get_queryset(self):
        return CompanyQuerySet(
            self.model,
            using=self._db,
        )

    def active(self):
        return self.get_queryset().active()

    def deleted(self):
        return self.get_queryset().deleted()

    def with_deleted(self):
        return self.get_queryset()

    def for_company(self, company):
        return self.active().for_company(company)

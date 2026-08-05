from typing import Any, Dict, Optional, Type

from django.db import models

from core.services.base_service import BaseService


class TenantService(BaseService):
    """
    Tenant-aware service with company validation.
    Uses CompanyManager.for_company() for querysets.
    """

    def __init__(self, company=None, user=None, request=None):
        super().__init__(company=company, user=user, request=request)
        self.validate_company()

    def validate_company(self):
        if self.company is None:
            raise ValueError("Company is required.")
        if not self.company.is_active:
            raise ValueError("Company is not active.")

    def get_queryset(self):
        return self.model.objects.for_company(self.company)

    def get_or_create(self, data: Dict[str, Any], defaults: Optional[Dict[str, Any]] = None):
        instance, created = self.model.objects.get_or_create(
            company=self.company,
            is_deleted=False,
            defaults=defaults,
            **data,
        )
        return instance, created

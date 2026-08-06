"""
Company service.

Central entry point for company lifecycle operations: status transitions,
settings/branding management and the onboarding workflow.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

from audit_logs.services.audit_log_service import AuditLogService

if TYPE_CHECKING:
    from accounts.models import User

from ..models import Company, CompanyOnboarding, CompanySettings, CompanyStatus


class CompanyService:
    """
    Business logic for tenant companies.

    Status is the single source of truth; ``is_active`` is kept in sync
    by ``Company.save()``. All state transitions are transactional and
    audited.
    """

    # ------------------------------------------------------------------
    # Status transitions
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def suspend(company: Company, user: Optional["User"] = None) -> Company:
        if company.is_suspended:
            return company
        company.status = CompanyStatus.SUSPENDED
        company.save(update_fields=["status", "is_active", "updated_at"])
        AuditLogService.log(
            action="company_suspended",
            resource="Company",
            resource_id=str(company.pk),
            resource_name=company.company_name,
            metadata={"company_id": company.pk},
            user=user,
            company=company,
        )
        return company

    @staticmethod
    @transaction.atomic
    def reactivate(company: Company, user: Optional["User"] = None) -> Company:
        company.status = CompanyStatus.ACTIVE
        company.save(update_fields=["status", "is_active", "updated_at"])
        AuditLogService.log(
            action="company_reactivated",
            resource="Company",
            resource_id=str(company.pk),
            resource_name=company.company_name,
            metadata={"company_id": company.pk},
            user=user,
            company=company,
        )
        return company

    @staticmethod
    @transaction.atomic
    def archive(company: Company, user: Optional["User"] = None) -> Company:
        company.status = CompanyStatus.ARCHIVED
        company.save(update_fields=["status", "is_active", "updated_at"])
        AuditLogService.log(
            action="company_archived",
            resource="Company",
            resource_id=str(company.pk),
            resource_name=company.company_name,
            metadata={"company_id": company.pk},
            user=user,
            company=company,
        )
        return company

    # ------------------------------------------------------------------
    # Settings / Branding
    # ------------------------------------------------------------------

    @staticmethod
    def get_or_create_settings(company: Company) -> CompanySettings:
        return CompanySettings.objects.get_or_create(company=company)[0]

    @staticmethod
    @transaction.atomic
    def update_settings(
        company: Company,
        data: Dict[str, Any],
        user: Optional["User"] = None,
    ) -> CompanySettings:
        settings = CompanyService.get_or_create_settings(company)
        changed = []
        for key, value in data.items():
            if hasattr(settings, key) and getattr(settings, key) != value:
                changed.append(key)
                setattr(settings, key, value)
        if changed:
            settings.save()
            AuditLogService.log(
                action="company_settings_updated",
                resource="CompanySettings",
                resource_id=str(settings.pk),
                resource_name=company.company_name,
                metadata={"updated_fields": changed},
                user=user,
                company=company,
            )
        return settings

    # ------------------------------------------------------------------
    # Onboarding
    # ------------------------------------------------------------------

    @staticmethod
    def get_or_create_onboarding(company: Company) -> CompanyOnboarding:
        return CompanyOnboarding.objects.get_or_create(company=company)[0]

    @staticmethod
    @transaction.atomic
    def complete_onboarding_step(
        company: Company,
        step: str,
        value: bool = True,
        user: Optional["User"] = None,
    ) -> CompanyOnboarding:
        onboarding = CompanyService.get_or_create_onboarding(company)
        onboarding.complete_step(step, value)
        AuditLogService.log(
            action="company_onboarding_step",
            resource="CompanyOnboarding",
            resource_id=str(onboarding.pk),
            resource_name=company.company_name,
            metadata={
                "step": step,
                "value": value,
                "progress": onboarding.progress,
            },
            user=user,
            company=company,
        )
        return onboarding

    @staticmethod
    def get_company_context(company: Company) -> Dict[str, Any]:
        """
        Assemble the public tenant context for a company: core record,
        settings/branding and onboarding progress.
        """
        settings = CompanyService.get_or_create_settings(company)
        onboarding = CompanyService.get_or_create_onboarding(company)
        return {
            "company": company,
            "settings": settings,
            "onboarding": onboarding,
            "onboarding_progress": onboarding.progress,
            "onboarding_completed": onboarding.is_completed,
        }

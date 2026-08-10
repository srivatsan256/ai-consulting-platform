"""
Quota Middleware Service
========================

Provides helpers for enforcing tenant quotas at the service level.

These are thin wrappers around ``subscriptions.services.usage_service``
that views and signal handlers can call without importing the full
subscriptions module directly.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from companies.models import Company


class QuotaMiddlewareService:
    """
    Convenience façade for tenant quota checks and usage recording.
    """

    @staticmethod
    def check_project_quota(company: "Company") -> None:
        """
        Raise ``ValidationError`` when the company has reached its project limit.
        """
        from projects.models import Project
        from subscriptions.services.usage_service import QuotaService

        if QuotaService.get_active_subscription(company) is None:
            return

        count = Project.objects.filter(company=company, is_active=True).count()
        QuotaService.check(company, "projects", count)

    @staticmethod
    def check_user_quota(company: "Company", new_users: int = 1) -> None:
        """
        Raise ``ValidationError`` when adding ``new_users`` would exceed the plan limit.
        """
        from subscriptions.services.usage_service import QuotaService

        if QuotaService.get_active_subscription(company) is None:
            return

        current = QuotaService.count_active_users(company)
        QuotaService.check(company, "users", current + new_users - 1)

    @staticmethod
    def check_storage_quota(company: "Company", additional_bytes: int = 0) -> None:
        """
        Raise ``ValidationError`` when uploading would exceed the storage limit.
        """
        from file_management.models import company_storage_usage
        from subscriptions.services.usage_service import QuotaService

        if QuotaService.get_active_subscription(company) is None:
            return

        total_bytes = company_storage_usage(company) + additional_bytes
        total_gb = total_bytes / (1024 ** 3)
        QuotaService.check(company, "storage_gb", total_gb)

    @staticmethod
    def check_ai_quota(company: "Company") -> None:
        """
        Raise ``ValidationError`` when the monthly AI request limit is reached.
        """
        from subscriptions.services.usage_service import QuotaService, UsageService

        if QuotaService.get_active_subscription(company) is None:
            return

        current = UsageService.get_period_usage(company, "ai_requests_per_month")
        QuotaService.check(company, "ai_requests_per_month", current)

    @staticmethod
    def record_ai_usage(company: "Company", quantity: int = 1) -> None:
        """Record one or more AI requests for the billing period."""
        from subscriptions.services.usage_service import UsageService

        UsageService.record(company, "ai_requests_per_month", quantity)

    @staticmethod
    def get_quota_summary(company: "Company") -> dict:
        """
        Return a dict summarising limits, current usage, and headroom
        for all plan resources.
        """
        from subscriptions.services.usage_service import QuotaService

        return QuotaService.get_report(company)

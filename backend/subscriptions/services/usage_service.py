"""
Usage tracking and tenant quota services.

UsageService records monthly-aggregated feature/resource usage per company
and reports it back. QuotaService enforces subscription plan limits
against live resource counts using the plan's ``max_<resource>`` fields.
"""

from __future__ import annotations

import calendar
from datetime import date
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone
from rest_framework.exceptions import ValidationError

if TYPE_CHECKING:
    from companies.models import Company
    from subscriptions.models import UsageRecord


def _period_start(reference: Optional[date] = None) -> date:
    """First day of the month that ``reference`` falls in."""
    reference = reference or timezone.localdate()
    return reference.replace(day=1)


def _period_end(reference: Optional[date] = None) -> date:
    """Last day of the month that ``reference`` falls in."""
    reference = reference or timezone.localdate()
    return reference.replace(day=calendar.monthrange(reference.year, reference.month)[1])


class UsageService:
    """
    Monthly usage counters keyed by (company, feature, month).
    """

    @staticmethod
    @transaction.atomic
    def record(
        company: "Company",
        feature: str,
        quantity: int = 1,
    ) -> "UsageRecord":
        """
        Increment usage for ``feature`` in the current billing month.
        """
        from subscriptions.models import UsageRecord

        period_start = _period_start()
        usage, _ = UsageRecord.objects.get_or_create(
            company=company,
            feature=feature,
            period_start=period_start,
        )
        UsageRecord.objects.filter(pk=usage.pk).update(
            quantity=F("quantity") + quantity,
            updated_at=timezone.now(),
        )
        usage.refresh_from_db()
        return usage

    @staticmethod
    def get_period_usage(
        company: "Company",
        feature: str,
        reference: Optional[date] = None,
    ) -> int:
        """
        Total usage for ``feature`` in the period containing ``reference``.
        """
        from subscriptions.models import UsageRecord

        total = (
            UsageRecord.objects.filter(
                company=company,
                feature=feature,
                period_start=_period_start(reference),
            ).aggregate(total=Sum("quantity"))["total"]
        )
        return total or 0

    @staticmethod
    def get_monthly_report(
        company: "Company",
        reference: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Usage report for every tracked feature in the current period.
        """
        from subscriptions.models import UsageRecord

        records = UsageRecord.objects.filter(
            company=company,
            period_start=_period_start(reference),
        ).order_by("feature")
        return [
            {
                "feature": record.feature,
                "quantity": record.quantity,
                "period_start": record.period_start.isoformat(),
                "period_end": _period_end(reference).isoformat(),
            }
            for record in records
        ]


class QuotaService:
    """
    Enforces subscription plan limits against live resource counts.
    """

    @staticmethod
    def get_active_subscription(company: "Company"):
        from subscriptions.models import CompanySubscription, SubscriptionStatus

        return (
            CompanySubscription.objects.filter(
                company=company,
                status__in=[SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING],
            )
            .select_related("plan")
            .order_by("-created_at")
            .first()
        )

    @staticmethod
    def get_limit(company: "Company", resource: str) -> Optional[int]:
        subscription = QuotaService.get_active_subscription(company)
        if subscription is None:
            return None
        return getattr(subscription.plan, f"max_{resource}", None)

    @staticmethod
    def count_active_users(company: "Company") -> int:
        """
        Active tenant headcount: active company members plus pending
        invitations. Used to enforce the plan's ``max_users`` limit for
        both direct membership creation and invitation flows.
        """
        from company_members.models import CompanyMember, UserInvitation

        members = CompanyMember.objects.filter(
            company=company,
            is_active=True,
        ).count()
        pending = UserInvitation.objects.filter(
            company=company,
            status="pending",
        ).count()
        return members + pending

    @staticmethod
    def check(company: "Company", resource: str, current_count: int) -> bool:
        """
        Raise a ``ValidationError`` when ``current_count`` meets or exceeds
        the plan limit for ``resource``.
        """
        subscription = QuotaService.get_active_subscription(company)
        if subscription is None:
            raise ValidationError(
                "Active subscription required to use this resource."
            )
        subscription.check_limit(resource, current_count)
        return True

    @staticmethod
    def get_report(company: "Company") -> Dict[str, Any]:
        """
        Quota overview: plan limits and recorded usage for each resource.
        """
        subscription = QuotaService.get_active_subscription(company)
        if subscription is None:
            return {"plan": None, "quotas": []}

        plan = subscription.plan
        resources = ["projects", "users", "storage_gb", "ai_requests_per_month"]
        quotas = []
        for resource in resources:
            limit = getattr(plan, f"max_{resource}", None)
            if limit is None:
                continue
            usage = (
                UsageService.get_period_usage(company, resource)
                if resource == "ai_requests_per_month"
                else None
            )
            quotas.append(
                {
                    "resource": resource,
                    "limit": limit,
                    "usage": usage,
                }
            )
        return {
            "plan": plan.code,
            "quotas": quotas,
        }

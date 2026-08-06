"""
Feature flag service.

Canonical resolution of whether a feature is available to a tenant.

Precedence:
    1. ``CompanyFeatureOverride`` -- authoritative per-company toggle.
    2. Plan grant -- for ``is_plan_gated`` flags, ``allows_<code>`` on the
       tenant's active plan.
    3. Global flag -- ``FeatureFlag.is_active`` for non-gated flags.

Backward compatibility: when no ``FeatureFlag`` row exists for a code the
service falls back to the plan's ``allows_<code>`` toggle so existing
integrations keep working.
"""

from __future__ import annotations

from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from companies.models import Company
    from subscriptions.models import CompanySubscription


class FeatureFlagService:

    @staticmethod
    def is_enabled(
        company: "Company",
        code: str,
        subscription: Optional["CompanySubscription"] = None,
    ) -> bool:
        from subscriptions.models import (
            CompanyFeatureOverride,
            CompanySubscription,
            FeatureFlag,
            SubscriptionStatus,
        )

        flag = FeatureFlag.objects.filter(code=code).first()

        if flag is None:
            return FeatureFlagService._plan_grants(
                company, code, subscription
            )

        override = CompanyFeatureOverride.objects.filter(
            company=company,
            feature=flag,
        ).first()
        if override is not None:
            return override.is_enabled

        if not flag.is_active:
            return False

        if flag.is_plan_gated:
            return FeatureFlagService._plan_grants(
                company, code, subscription
            )

        return True

    @staticmethod
    def get_feature_map(company: "Company") -> Dict[str, bool]:
        from subscriptions.models import FeatureFlag

        flags = FeatureFlag.objects.all()
        return {flag.code: FeatureFlagService.is_enabled(company, flag.code) for flag in flags}

    @staticmethod
    def list_flags() -> List["FeatureFlag"]:
        from subscriptions.models import FeatureFlag

        return list(FeatureFlag.objects.all().order_by("code"))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _plan_grants(
        company: "Company",
        code: str,
        subscription: Optional["CompanySubscription"],
    ) -> bool:
        if subscription is None:
            subscription = FeatureFlagService._active_subscription(company)
        if subscription is None:
            return False
        return bool(getattr(subscription.plan, f"allows_{code}", False))

    @staticmethod
    def _active_subscription(company: "Company") -> Optional["CompanySubscription"]:
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

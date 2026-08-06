"""
Tenant enforcement wiring.

Thin helpers that let views enforce the tenant's subscription, feature
flags, plan quotas and usage tracking through the existing services
(``FeatureFlagService``, ``QuotaService``, ``UsageService``). Views use
these instead of duplicating subscription/feature/limit logic.
"""

from rest_framework.exceptions import PermissionDenied


class TenantEnforcement:
    """
    Entry point for enforcing tenant-level policies inside views.

    Usage::

        tenant = TenantEnforcement.require_subscription(request)
        TenantEnforcement.require_feature(request, "custom_rag")
        TenantEnforcement.check_quota(request, "projects", current_count)
        TenantEnforcement.record_usage(request, "ai_requests_per_month")
    """

    @staticmethod
    def require_tenant(request):
        """
        Return the resolved ``TenantContext`` or raise if the request has
        no company associated with the authenticated user.
        """
        tenant = getattr(request, "tenant", None)
        if not tenant or not tenant.company:
            raise PermissionDenied("No company associated with this user.")
        return tenant

    @staticmethod
    def require_subscription(request):
        """
        Return the ``TenantContext`` only when the tenant has a valid
        active (or trialing) subscription.
        """
        tenant = TenantEnforcement.require_tenant(request)
        if not tenant.subscription or not tenant.subscription.is_valid:
            raise PermissionDenied("Active subscription required for this feature.")
        return tenant

    @staticmethod
    def require_feature(request, feature_name):
        """
        Raise ``PermissionDenied`` when the feature is not enabled for the
        tenant (respects per-company overrides and plan grants).
        """
        from subscriptions.services.feature_flag_service import FeatureFlagService

        tenant = TenantEnforcement.require_subscription(request)
        if not FeatureFlagService.is_enabled(
            tenant.company,
            feature_name,
            subscription=tenant.subscription,
        ):
            raise PermissionDenied(
                f"Feature '{feature_name}' is not available on your current plan."
            )
        return tenant

    @staticmethod
    def check_quota(request, resource, current_count):
        """
        Raise a ``ValidationError`` when ``current_count`` meets or exceeds
        the tenant's plan limit for ``resource``.

        Fail-open when the tenant has no active subscription: without a plan
        there is no defined limit, so resource creation (e.g. during
        onboarding) is not blocked.
        """
        from subscriptions.services.usage_service import QuotaService

        tenant = TenantEnforcement.require_tenant(request)
        if QuotaService.get_active_subscription(tenant.company) is None:
            return tenant
        QuotaService.check(tenant.company, resource, current_count)
        return tenant

    @staticmethod
    def record_usage(request, feature, quantity=1):
        """
        Record usage for ``feature`` against the request's tenant.
        No-op when the request has no resolved tenant.
        """
        from subscriptions.services.usage_service import UsageService

        tenant = getattr(request, "tenant", None)
        if tenant and tenant.company:
            UsageService.record(tenant.company, feature, quantity)

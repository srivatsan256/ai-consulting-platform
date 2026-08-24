"""
Tenant enforcement wiring.

Subscription and quota enforcement has been removed. These helpers keep
their original signatures so views and services continue to work, but
they no longer gate anything.
"""

from rest_framework.exceptions import PermissionDenied


class TenantEnforcement:
    """
    Entry point for tenant-level policies inside views.

    Usage::

        tenant = TenantEnforcement.require_subscription(request)
        tenant = TenantEnforcement.require_tenant(request)
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
        """No-op: subscriptions were removed. Returns the tenant context."""
        return TenantEnforcement.require_tenant(request)

    @staticmethod
    def require_feature(request, feature_name):
        """No-op: all features are enabled."""
        return getattr(request, "tenant", None)

    @staticmethod
    def check_quota(request, resource, current_count):
        """No-op: quotas were removed. Returns the tenant context."""
        return getattr(request, "tenant", None)

    @staticmethod
    def check_ai_quota(request):
        """No-op: quotas were removed. Returns the tenant context."""
        return getattr(request, "tenant", None)

    @staticmethod
    def check_storage_quota(request, additional_bytes=0):
        """No-op: quotas were removed. Returns the tenant context."""
        return getattr(request, "tenant", None)

    @staticmethod
    def record_usage(request, feature, quantity=1):
        """No-op: usage tracking was removed."""
        return None

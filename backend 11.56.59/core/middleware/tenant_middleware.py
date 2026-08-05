from core.middleware.tenant_context import TenantContext


class TenantMiddleware:
    """
    Resolves tenant context from JWT claim or primary membership.
    Lightweight - only populates request.tenant, no business logic.

    Business logic (subscription validation, feature checks) belongs in:
    - Permission classes
    - Service layer
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = TenantContext()

        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            membership = self._get_primary_membership(user)
            if membership:
                subscription = self._get_subscription(membership.company)
                request.tenant = TenantContext(
                    company=membership.company,
                    membership=membership,
                    role=membership.role,
                    subscription=subscription,
                    features=self._get_features(subscription),
                )

        return self.get_response(request)

    def _get_primary_membership(self, user):
        """
        Get primary membership for user.
        Could be extended to use JWT claim (X-Company-ID header) first.
        """
        from company_members.models import CompanyMember

        return CompanyMember.objects.primary_for_user(user)

    def _get_subscription(self, company):
        """
        Get active subscription for company.
        """
        from subscriptions.models import CompanySubscription, SubscriptionStatus

        return (
            CompanySubscription.objects.filter(
                company=company,
                status__in=[SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING],
            )
            .select_related("plan")
            .first()
        )

    def _get_features(self, subscription):
        """
        Get feature flags from subscription plan.
        """
        if not subscription:
            return {}

        plan = subscription.plan
        return {
            "custom_rag": getattr(plan, "allows_custom_rag", False),
            "advanced_reports": getattr(plan, "allows_advanced_reports", False),
            "custom_integrations": getattr(plan, "allows_custom_integrations", False),
        }
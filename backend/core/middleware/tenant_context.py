class TenantContext:
    """
    Holds the resolved tenant context for the current request.
    Populated by TenantMiddleware from JWT claim or primary membership.

    Usage:
        request.tenant.company
        request.tenant.membership
        request.tenant.role
        request.tenant.subscription
        request.tenant.features
    """

    def __init__(
        self,
        company=None,
        membership=None,
        role=None,
        subscription=None,
        features=None,
    ):
        self.company = company
        self.membership = membership
        self.role = role
        self.subscription = subscription
        self.features = features or {}

    @property
    def is_authenticated(self):
        return self.company is not None

    def has_feature(self, feature_name):
        """
        Check if a feature is enabled for this tenant.
        """
        if not self.subscription:
            return False
        return getattr(self.subscription.plan, f"allows_{feature_name}", False)

    def __repr__(self):
        if self.company:
            return f"<TenantContext company={self.company.company_name}>"
        return "<TenantContext unauthenticated>"

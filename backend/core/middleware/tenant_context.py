class TenantContext:
    """
    Holds the resolved tenant context for the current request.
    Populated by TenantMiddleware from JWT claim or primary membership.

    Usage:
        request.tenant.company
        request.tenant.membership
        request.tenant.role
    """

    def __init__(
        self,
        company=None,
        membership=None,
        role=None,
    ):
        self.company = company
        self.membership = membership
        self.role = role

    @property
    def is_authenticated(self):
        return self.company is not None

    def has_feature(self, feature_name):
        """
        All features are enabled; subscriptions were removed.
        """
        return True

    def __repr__(self):
        if self.company:
            return f"<TenantContext company={self.company.company_name}>"
        return "<TenantContext unauthenticated>"

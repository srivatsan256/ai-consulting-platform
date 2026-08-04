class CompanyMiddleware:
    """
    Simplified - context resolution moved to TenantMiddleware.
    This middleware is now a pass-through for backward compatibility.
    Can be removed after all modules are migrated to use request.tenant.
    """

    EXCLUDED_PATHS = (
        "/admin/",
        "/api/auth/login/",
        "/api/auth/register/",
        "/api/auth/token/",
        "/api/auth/token/refresh/",
        "/api/memberships/",
        "/schema/",
        "/swagger/",
        "/redoc/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip excluded URLs
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return self.get_response(request)

        # Context already resolved by TenantMiddleware
        # Validation happens in permission classes and service layer
        return self.get_response(request)
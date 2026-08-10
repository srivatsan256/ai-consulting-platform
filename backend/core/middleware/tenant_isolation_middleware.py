"""
Tenant Isolation Middleware
===========================

Enforces strict cross-tenant data isolation at the HTTP layer.

- Ensures every authenticated request resolves to exactly one tenant.
- Rejects requests that carry a company context which does not match
  an active membership for the authenticated user.
- Attaches ``request.tenant_validated = True`` so downstream code can
  trust the context was verified here.
"""

from django.http import JsonResponse


# Paths that are allowed without an active company context.
_OPEN_PATHS = (
    "/admin/",
    "/api/auth/",
    "/api/health/",
    "/api/docs/",
    "/api/schema/",
    "/password-reset/",
)


class TenantIsolationMiddleware:
    """
    Post-authentication tenant validation.

    Runs *after* TenantMiddleware so ``request.tenant`` is already populated.
    Rejects authenticated requests that have no resolved company (unenrolled
    users, stale tokens) while leaving public/auth paths unrestricted.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant_validated = False

        # Skip open paths.
        if any(request.path.startswith(p) for p in _OPEN_PATHS):
            request.tenant_validated = True
            return self.get_response(request)

        user = getattr(request, "user", None)

        # Unauthenticated requests fall through to DRF permission classes.
        if user is None or not getattr(user, "is_authenticated", False):
            return self.get_response(request)

        # Superusers bypass tenant isolation (platform admin operations).
        if getattr(user, "is_superuser", False):
            request.tenant_validated = True
            return self.get_response(request)

        tenant = getattr(request, "tenant", None)
        if tenant is None or not getattr(tenant, "company", None):
            return JsonResponse(
                {
                    "success": False,
                    "message": "No active company membership found for this user.",
                    "errors": {
                        "detail": (
                            "You must belong to at least one active company. "
                            "Please contact your administrator."
                        )
                    },
                },
                status=403,
            )

        # Validate that the resolved company is still active.
        if not tenant.company.is_active:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Your company account is suspended or archived.",
                    "errors": {"detail": "Company inactive."},
                },
                status=403,
            )

        request.tenant_validated = True
        return self.get_response(request)

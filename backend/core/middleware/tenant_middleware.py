"""
Tenant Middleware
=================

Thin middleware that resolves the tenant context for every request by
delegating to :class:`core.services.tenant_resolution_service.TenantResolutionService`.

No business logic lives here. The service decides which company the
request is acting on (JWT claim -> ``X-Company-ID`` header -> primary
membership) and populates both ``request.tenant`` and the thread-local
current tenant. Validation and enforcement happen in permission classes
and the service layer.
"""

from core.middleware.tenant_context import TenantContext
from core.services.tenant_resolution_service import TenantResolutionService


class TenantMiddleware:
    """
    Resolves and attaches the ``TenantContext`` to ``request.tenant``.

    The ``X-Company-ID`` header is whitelisted per-request so it cannot
    be used to forge a context on public endpoints; an unauthenticated
    request always receives an empty ``TenantContext``.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.resolution_service = TenantResolutionService()

    def __call__(self, request):
        context = self.resolution_service.resolve_for_request(request)

        if not isinstance(context, TenantContext):
            context = TenantContext()

        request.tenant = context
        return self.get_response(request)

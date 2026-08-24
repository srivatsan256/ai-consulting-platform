"""
Tenant Resolution Service
=========================

Central entry point for resolving the current tenant (Company) for an
authenticated request and building the request-level ``TenantContext``
that every other layer (middleware, permissions, mixins, viewsets,
services) consumes via ``request.tenant``.

Resolution precedence:
    1. JWT claim ``company_id`` -- stateless, set at login and on
       company switch (see ``authentication.serializers``).
    2. ``X-Company-ID`` header -- explicit override for multi-company
       users that want to address a non-primary company without re-login.
    3. Primary ``CompanyMember`` -- fallback when neither the claim nor
       the header is present.

This service is the single source of truth for "which company is this
request acting on". Keeping the logic here instead of inside middleware
or permission classes guarantees the same context everywhere and makes
it testable in isolation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from django.utils.functional import cached_property

from core.middleware.tenant_context import TenantContext
from core.tenant.context import set_current_tenant

if TYPE_CHECKING:
    from accounts.models import User
    from companies.models import Company
    from company_members.models import CompanyMember

    from django.http import HttpRequest

COMPANY_ID_HEADER = "X-Company-ID"


class TenantResolutionService:
    """
    Resolves and materializes the tenant context for a request.

    Usage::

        service = TenantResolutionService()
        context = service.resolve_for_request(request)
        request.tenant = context
    """

    def resolve_for_request(self, request: "HttpRequest") -> TenantContext:
        """
        Resolve the tenant for an authenticated request and sync the
        thread-local current tenant.

        When the user is anonymous or unauthenticated an empty
        ``TenantContext`` is returned and the thread-local tenant is
        cleared.
        """
        user = getattr(request, "user", None)

        if user is None or not getattr(user, "is_authenticated", False):
            context = TenantContext()
            self._sync_context(context)
            return context

        company_id = self._company_id_from_request(request)
        context = self.resolve_for_user(user=user, company_id=company_id)
        self._sync_context(context)
        return context

    def resolve_for_user(
        self,
        user: "User",
        company_id: Optional[int] = None,
    ) -> TenantContext:
        """
        Build the ``TenantContext`` for a user, honouring the optional
        ``company_id`` (from JWT claim or ``X-Company-ID`` header) before
        falling back to the user's primary membership.
        """
        membership = self._resolve_membership(user=user, company_id=company_id)

        if membership is None:
            context = TenantContext()
            self._sync_context(context)
            return context

        context = TenantContext(
            company=membership.company,
            membership=membership,
            role=membership.role,
        )
        self._sync_context(context)
        return context

    # ------------------------------------------------------------------
    # Resolution steps
    # ------------------------------------------------------------------

    def _company_id_from_request(self, request: "HttpRequest") -> Optional[int]:
        """
        Prefer the ``X-Company-ID`` header, then the JWT ``company_id``
        claim. ``request.auth`` is the validated token when
        ``CustomJWTAuthentication`` authenticates the request.
        """
        header_value = request.headers.get(COMPANY_ID_HEADER)
        if header_value:
            try:
                return int(header_value)
            except (TypeError, ValueError):
                return None

        auth = getattr(request, "auth", None)
        if auth is not None:
            return auth.get("company_id")

        return None

    def _resolve_membership(
        self,
        user: "User",
        company_id: Optional[int],
    ) -> Optional["CompanyMember"]:
        """
        Resolve the active ``CompanyMember``.

        A requested ``company_id`` takes precedence but only when it maps
        to an active membership; otherwise we fall back to the primary
        membership so stale claims never lock a user out.
        """
        from company_members.models import CompanyMember

        memberships = (
            CompanyMember.objects.filter(user=user, is_active=True)
            .select_related("company", "role")
            .filter(company__is_active=True)
            .order_by("-is_primary", "-joined_at")
        )

        if company_id is not None:
            membership = memberships.filter(company_id=company_id).first()
            if membership is not None:
                return membership

        return memberships.first()

    # ------------------------------------------------------------------
    # Side effects
    # ------------------------------------------------------------------

    def _sync_context(self, context: TenantContext) -> None:
        """
        Mirror the resolved company into the thread-local tenant so
        non-request code (signals, tasks, shell) can retrieve it via
        ``core.tenant.context.get_current_tenant``.
        """
        set_current_tenant(context.company)

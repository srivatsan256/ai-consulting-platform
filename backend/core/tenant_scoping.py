"""
Tenant scoping for DRF viewsets
===============================

Forces every queryset through the current tenant (``request.tenant.company``)
so cross-tenant data access is impossible regardless of how a view declares
its queryset.

The company lookup path is auto-detected from the queryset's model by walking
its forward relations:

    - ``company``                        -> ``company=<tenant>``
    - ``project``                        -> ``project__company=<tenant>``
    - ``task``                           -> ``task__project__company=<tenant>``
    - ``workflow``                       -> ``workflow__project__company=<tenant>``
    - ``conversation``                   -> ``conversation__project__company=<tenant>``
    - ``knowledge_base``                 -> ``knowledge_base__project__company=<tenant>``
    - ``review``                         -> ``review__project__company=<tenant>``
    - ``issue``                          -> ``issue__project__company=<tenant>``
    - ``assessment``                     -> ``assessment__project__company=<tenant>``

Views that cannot be auto-detected may declare ``tenant_lookup_path``
explicitly. When no path can be derived the queryset is emptied (fail closed)
instead of leaking rows.

Views that already override ``get_queryset`` should build on
``super().get_queryset()`` so this mixin can scope the result, e.g.::

    class TaskAttachmentViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
        def get_queryset(self):
            return super().get_queryset().filter(...)
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from django.db import models
from rest_framework.exceptions import PermissionDenied

if TYPE_CHECKING:
    from django.db.models import Model, QuerySet


#: FK name -> company lookup path for one-hop relations that lead to a project.
_SINGLE_HOP_PATHS = {
    "project": "project__company",
    "task": "task__project__company",
    "workflow": "workflow__project__company",
    "conversation": "conversation__project__company",
    "knowledge_base": "knowledge_base__project__company",
    "review": "review__project__company",
    "issue": "issue__project__company",
    "assessment": "assessment__project__company",
    "meeting": "meeting__project__company",
}


def detect_tenant_lookup_path(model: "Model") -> Optional[str]:
    """
    Derive the company lookup path for ``model`` from its forward relations.

    Returns ``None`` when no tenant-scoping chain can be derived.
    """
    if model is None:
        return None

    forward_fk_names = {
        f.name
        for f in model._meta.get_fields()
        if f.is_relation
        and f.concrete
        and not f.auto_created
        and (f.many_to_one or f.one_to_one)
    }

    if "company" in forward_fk_names:
        return "company"
    if "project" in forward_fk_names:
        return "project__company"
    for fk, path in _SINGLE_HOP_PATHS.items():
        if fk in forward_fk_names:
            return path
    return None


def scope_queryset(
    queryset: "QuerySet",
    company,
    lookup_path: Optional[str] = None,
) -> "QuerySet":
    """
    Return ``queryset`` filtered to ``company`` using ``lookup_path`` (or an
    auto-detected one). Fails closed with an empty queryset when the model
    cannot be scoped.
    """
    path = lookup_path or detect_tenant_lookup_path(queryset.model)
    if path is None:
        return queryset.none()
    return queryset.filter(**{path: company})


class TenantScopedViewSetMixin:
    """
    Mixin that tenant-scopes a viewset's ``get_queryset``.

    Place it before ``viewsets.ModelViewSet`` in the base list::

        class DocumentViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
            queryset = Document.objects.all()
    """

    #: Optional explicit lookup path; auto-detected when ``None``.
    tenant_lookup_path: Optional[str] = None

    def get_queryset(self):
        queryset = super().get_queryset()

        user = getattr(self.request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return queryset.none()

        tenant = getattr(self.request, "tenant", None)
        if tenant is None or getattr(tenant, "company", None) is None:
            return queryset.none()

        return scope_queryset(
            queryset,
            tenant.company,
            lookup_path=self.tenant_lookup_path,
        )

    def _validate_tenant_scoped_fks(self, data):
        """
        Reject writes that point a tenant-scoped foreign key at an object
        owned by another company.

        Reads already flow through the scoped ``get_queryset``, but
        list-create/update accept FK ids directly, so a POST body could
        reference a ``project``/``task``/``meeting``/... that belongs to a
        different tenant. This closes that cross-tenant write vector for
        every viewset using the mixin.
        """
        tenant = getattr(self.request, "tenant", None)
        company = getattr(tenant, "company", None)
        if company is None:
            return

        for field_name, value in data.items():
            if value is None or not isinstance(value, models.Model):
                continue
            path = detect_tenant_lookup_path(value.__class__)
            if path is None:
                continue
            node = value
            for lookup in path.split("__"):
                node = getattr(node, lookup, None)
                if node is None:
                    break
            if node is not None and node.pk != company.pk:
                raise PermissionDenied(
                    f"{field_name} does not belong to your company."
                )

    def perform_create(self, serializer):
        self._validate_tenant_scoped_fks(serializer.validated_data)
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        self._validate_tenant_scoped_fks(serializer.validated_data)
        return super().perform_update(serializer)

"""Role-based authorization primitives.

The permission chain documented on ``CompanyMember`` is:

    IsAuthenticated -> IsCompanyMember -> IsProjectMember -> RolePermission

``RolePermission`` resolves the acting user's role from ``request.tenant``
(which the tenant middleware resolves from the active membership) and checks
it against the feature-level rows in ``permissions.Permission``. Views opt in
by declaring ``permission_feature`` (and optionally ``permission_action``);
without a feature the view only requires an authenticated company membership.
"""

from rest_framework.permissions import BasePermission

#: Roles that bypass feature checks and manage company-level authorization.
MANAGER_ROLE_KEYS = ("super_admin", "company_admin", "client_admin")

#: HTTP method -> feature permission flag.
ACTION_BY_METHOD = {
    "GET": "view",
    "POST": "create",
    "PUT": "update",
    "PATCH": "update",
    "DELETE": "delete",
}


def has_feature_permission(role, feature, action):
    """
    Return True when ``role`` may perform ``action`` on ``feature``.

    ``super_admin`` always passes (fail-open for the platform owner); every
    other role is checked against ``permissions.Permission`` and fails closed
    when no permission row exists.
    """
    if role is None:
        return False

    role_key = getattr(role, "role_key", None)
    if role_key == "super_admin":
        return True

    if not getattr(role, "is_active", True):
        return False

    from permissions.models import Permission

    permission = (
        Permission.objects.filter(role=role, feature=feature)
        .only(
            "can_view",
            "can_create",
            "can_update",
            "can_delete",
            "can_review",
            "can_approve",
            "can_export",
        )
        .first()
    )
    if permission is None:
        return False

    return bool(getattr(permission, f"can_{action}", False))


def is_manager_role(role):
    """Return True when ``role`` grants company-level authorization control."""
    return (
        role is not None
        and getattr(role, "role_key", None) in MANAGER_ROLE_KEYS
    )


class RolePermission(BasePermission):
    """
    View-level RBAC against the acting user's role.

    Usage::

        class DocumentViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, RolePermission]
            permission_feature = "document_management"
            # permission_action = "view"  # optional; defaults by HTTP method

    The user must belong to an active company (``request.tenant.role`` is
    resolved from the active membership). ``super_admin`` bypasses the feature
    check; other roles are compared against their ``permissions.Permission``
    row for the declared feature.
    """

    def has_permission(self, request, view):
        tenant = getattr(request, "tenant", None)
        role = getattr(tenant, "role", None)

        if role is None:
            return False

        feature = getattr(view, "permission_feature", None)
        if feature is None:
            return True

        action = getattr(view, "permission_action", None)
        if action is None:
            action = ACTION_BY_METHOD.get(request.method) # type: ignore
            if action is None:
                return False

        return has_feature_permission(role, feature, action)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

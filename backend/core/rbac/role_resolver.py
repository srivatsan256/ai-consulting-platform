"""Role and permission resolution for the acting user.

Resolves the acting user's role and the feature-level permission rows granted
to that role from the request-level ``TenantContext``. This is the shared
source for ``GET /roles/mine/`` and any UI that needs to render the current
user's authorization matrix.
"""

from typing import Optional

from authentication.serializers import Role


def resolve_role(request):
    """
    Return the acting user's ``Role`` for the tenant company, or None when
    the user has no active company membership.
    """
    tenant = getattr(request, "tenant", None)
    if tenant is None:
        return None
    return getattr(tenant, "role", None)


def permissions_for_role(role):
    """
    Return the ``permissions.Permission`` queryset for ``role`` (ordered by
    feature). Empty when ``role`` is None.
    """
    if role is None:
        return []
    from permissions.models import Permission

    return Permission.objects.filter(role=role).order_by("feature")


def my_role_context(request):
    """
    Build the role + permissions dict for the acting user, suitable for
    serialization by ``roles.serializers.MyRoleSerializer``.

    Returns None when the user is not a member of any company.
    """
    role = resolve_role(request)
    if role is None:
        return None

    return {
        "id": role.id,
        "role_key": role.role_key,
        "display_name": role.display_name,
        "permissions": permissions_for_role(role),
    }


def role_by_key(role_key: str) -> Optional["Role"]:
    """
    Return the active ``Role`` matching ``role_key``, or None.

    Imported lazily so ``core`` never depends on the ``roles`` app at import
    time.
    """
    from roles.models import Role

    return Role.objects.filter(role_key=role_key, is_active=True).first()

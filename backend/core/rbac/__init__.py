"""Role-based access control (RBAC) for the AI Consulting Platform.

Public API:

* ``has_feature_permission(role, feature, action)`` -- check a single
  role against the feature permission matrix.
* ``is_manager_role(role)`` -- True for ``super_admin``/``company_admin``.
* ``RolePermission`` -- DRF view-level RBAC permission class.
* ``CanManageDepartmentMembers`` / ``IsDepartmentHeadOrMember`` -- DRF
  department-scoped permission classes.
* ``resolve_role`` / ``permissions_for_role`` / ``my_role_context`` /
  ``role_by_key`` -- role + permission resolution helpers.
"""

from core.rbac.permissions import (
    ACTION_BY_METHOD,
    MANAGER_ROLE_KEYS,
    RolePermission,
    has_feature_permission,
    is_manager_role,
)
from core.rbac.role_resolver import (
    my_role_context,
    permissions_for_role,
    resolve_role,
    role_by_key,
)
from core.rbac.department_permissions import (
    CanManageDepartmentMembers,
    IsDepartmentHeadOrMember,
)

__all__ = [
    "ACTION_BY_METHOD",
    "MANAGER_ROLE_KEYS",
    "RolePermission",
    "has_feature_permission",
    "is_manager_role",
    "CanManageDepartmentMembers",
    "IsDepartmentHeadOrMember",
    "my_role_context",
    "permissions_for_role",
    "resolve_role",
    "role_by_key",
]

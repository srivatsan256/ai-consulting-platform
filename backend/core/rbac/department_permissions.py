"""Department-scoped authorization.

Access model for department data:

    super_admin / company_admin  -> all departments in the company
    department head              -> their own department
    department member            -> their own department(s)
    everyone else                -> denied
"""

from rest_framework.permissions import BasePermission

from core.rbac.permissions import is_manager_role


class CanManageDepartmentMembers(BasePermission):
    """
    Grant department-member management to company admins and the department
    head. Management covers create, partial_update and destroy; non-write
    actions pass through to object-level checks.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        tenant = getattr(request, "tenant", None)
        role = getattr(tenant, "role", None)

        if is_manager_role(role):
            return True

        if view.action == "create": # type: ignore
            department_id = (
                request.data.get("department")
                if isinstance(request.data, dict)
                else None
            )
            if department_id is None:
                return False
            from departments.models import Department

            department = Department.objects.filter(pk=department_id).first()
            return department is not None and department.head_id == user.id # type: ignore

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        tenant = getattr(request, "tenant", None)
        role = getattr(tenant, "role", None)

        if is_manager_role(role):
            return True

        if view.action in ("destroy", "partial_update", "update"): # type: ignore
            return obj.department.head_id == user.id # type: ignore

        return False


class IsDepartmentHeadOrMember(BasePermission):
    """
    Allow reads when the user is the department head, an active member of the
    department, or a company admin/super admin.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        tenant = getattr(request, "tenant", None)
        role = getattr(tenant, "role", None)

        if is_manager_role(role):
            return True

        if obj.department.head_id == user.id: # type: ignore
            return True

        return obj.members.filter(user=user, is_active=True).exists()

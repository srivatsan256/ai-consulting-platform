"""Role assignment service.

Assigning a role to a user updates the single source of truth
(``CompanyMember.role``) and records the change in ``RoleAssignment`` for
auditing. All validation for who-may-assign-what lives here so the same rules
are enforced from the API and any future internal callers.
"""

from django.db import transaction

from rest_framework.exceptions import PermissionDenied, ValidationError

from roles.models import Role, RoleAssignment
from core.rbac.permissions import is_manager_role


class RoleAssignmentService:
    """Validated role assignment for a user within a company."""

    @staticmethod
    def assign(*, actor, user, company, role, previous_role=None):
        """
        Assign ``role`` to ``user`` within ``company`` on behalf of ``actor``.

        Raises:
            PermissionDenied: actor may not manage roles in the company.
            ValidationError: role inactive/unknown, target not a member, or
                an actor (non-super-admin) trying to change their own role.
        """
        if role is None or not role.is_active:
            raise ValidationError({"role": "Role must be active and valid."})

        actor_membership = (
            actor.company_memberships.filter(
                company=company,
                is_active=True,
            )
            .select_related("role")
            .first()
        )

        if actor_membership is None or not is_manager_role(actor_membership.role):
            raise PermissionDenied(
                "Only a company admin or super admin can assign roles."
            )

        if actor == user and actor_membership.role.role_key != "super_admin":
            raise PermissionDenied(
                "You cannot change your own role. Ask a super admin instead."
            )

        membership = (
            user.company_memberships.filter(company=company, is_active=True)
            .select_related("role")
            .first()
        )
        if membership is None:
            raise ValidationError(
                {"user": "User is not an active member of this company."}
            )

        if previous_role is None:
            previous_role = membership.role

        if membership.role_id != role.id:
            with transaction.atomic():
                membership.role = role
                membership.save(update_fields=["role", "updated_at"])
                assignment = RoleAssignment.objects.create(
                    user=user,
                    company=company,
                    role=role,
                    previous_role=previous_role,
                    assigned_by=actor,
                )
            return assignment

        return None

    @staticmethod
    def history_for_company(company):
        """Return the assignment audit trail for ``company``."""
        return (
            RoleAssignment.objects.filter(company=company)
            .select_related("user", "role", "previous_role", "assigned_by")
            .order_by("-created_at")
        )

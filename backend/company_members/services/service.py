from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

from ..models import CompanyMember


class MembershipService:
    """
    Service for managing company memberships.
    Handles business logic for membership operations.
    """

    def __init__(self, user=None):
        self.user = user

    def get_user_memberships(self, user=None):
        target_user = user or self.user
        return CompanyMember.objects.for_user(target_user)

    def get_primary_membership(self, user=None):
        target_user = user or self.user
        return CompanyMember.objects.primary_for_user(target_user)

    def switch_company(self, company_id):
        """
        Switch user's active company.
        Returns the membership for the target company.
        """
        try:
            membership = CompanyMember.objects.get(
                user=self.user,
                company_id=company_id,
                is_active=True,
            )
        except CompanyMember.DoesNotExist:
            raise ValidationError("You are not a member of this company.")

        # Set as primary
        CompanyMember.objects.set_primary(self.user, membership.company)

        return membership

    def invite_member(self, email, company, role):
        """
        Invite a new member to the company.
        """
        from accounts.models import User

        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": email.split("@")[0]},
        )

        membership = CompanyMember.objects.add_member(
            user=user,
            company=company,
            role=role,
        )

        return membership

    def remove_member(self, user, company):
        """
        Deactivate a member from the company.
        """
        return CompanyMember.objects.deactivate_member(user, company)

    def update_role(self, user, company, new_role):
        """
        Update a member's role.
        """
        try:
            membership = CompanyMember.objects.get(
                user=user,
                company=company,
                is_active=True,
            )
            membership.role = new_role
            membership.save(update_fields=["role"])
            return membership
        except CompanyMember.DoesNotExist:
            raise ValidationError("Member not found in this company.")

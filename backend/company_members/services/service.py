from datetime import timedelta

from django.db import transaction
from django.utils import timezone
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


class InvitationService:
    """
    Handles inviting users to join a company via email invitations.
    """

    INVITE_TTL_DAYS = 7

    def __init__(self, user=None):
        self.user = user

    def create_invitation(self, email, company, role, department=None):
        """
        Create a pending invitation for ``email`` in ``company``.
        """
        from accounts.models import User

        from ..models import UserInvitation

        email = (email or "").strip().lower()
        if not email:
            raise ValidationError({"email": "Email is required."})

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                {
                    "email": (
                        "A user with this email already exists. Add them as a "
                        "member directly instead."
                    )
                }
            )

        if UserInvitation.objects.filter(
            company=company,
            email=email,
            status="pending",
        ).exists():
            raise ValidationError(
                {"email": "A pending invitation already exists for this email."}
            )

        invitation = UserInvitation.objects.create(
            company=company,
            email=email,
            role=role,
            department=department,
            invited_by=self.user,
            token=UserInvitation.generate_token(),
            expires_at=timezone.now() + timedelta(days=self.INVITE_TTL_DAYS),
        )
        return invitation

    def accept_invitation(self, token, first_name, last_name, password):
        """
        Validate ``token`` and create the user + membership on acceptance.
        """
        from accounts.models import User

        from ..models import UserInvitation

        invitation = UserInvitation.objects.select_related(
            "company", "role"
        ).filter(token=token).first()
        if invitation is None:
            raise ValidationError({"token": "Invitation not found."})
        if invitation.status == "accepted":
            raise ValidationError(
                {"token": "This invitation has already been accepted."}
            )
        if invitation.status != "pending":
            raise ValidationError(
                {"token": "This invitation is no longer valid."}
            )
        if invitation.expires_at <= timezone.now():
            invitation.status = "expired"
            invitation.save(update_fields=["status"])
            raise ValidationError({"token": "This invitation has expired."})

        email = invitation.email
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                {"email": "A user with this email already exists."}
            )

        with transaction.atomic():
            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=(first_name or "").strip(),
                last_name=(last_name or "").strip(),
                password=password,
                is_active=True,
                is_email_verified=True,
            )
            CompanyMember.objects.get_or_create(
                user=user,
                company=invitation.company,
                defaults={
                    "role": invitation.role,
                    "is_primary": True,
                    "is_active": True,
                },
            )
            invitation.status = "accepted"
            invitation.accepted_at = timezone.now()
            invitation.save(update_fields=["status", "accepted_at"])

        return user, invitation

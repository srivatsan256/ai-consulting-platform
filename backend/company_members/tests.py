from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from company_members.models import CompanyMember, UserInvitation
from core.tests_helpers import (
    authenticate,
    create_company,
    create_member,
    create_user,
    get_role,
)


class CompanyMemberModelTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="member", email="member@example.com")
        self.company = create_company(name="Member Corp")

    def test_membership_is_unique_per_user_and_company(self):
        create_member(self.user, self.company)
        with self.assertRaises(Exception):
            create_member(self.user, self.company, is_primary=False)

    def test_primary_for_user_returns_primary_membership(self):
        other = create_company(name="Other Corp")
        create_member(self.user, self.company, is_primary=True)
        create_member(self.user, other, is_primary=False)
        primary = CompanyMember.objects.primary_for_user(self.user)
        self.assertEqual(primary.company, self.company)

    def test_for_user_excludes_inactive_memberships(self):
        membership = create_member(self.user, self.company)
        membership.is_active = False
        membership.save()
        self.assertEqual(
            CompanyMember.objects.for_user(self.user).count(),
            0,
        )

    def test_set_primary_switches_primary_flag(self):
        other = create_company(name="Switch Corp")
        create_member(self.user, self.company, is_primary=True)
        create_member(self.user, other, is_primary=False)
        CompanyMember.objects.set_primary(self.user, other)
        primary = CompanyMember.objects.primary_for_user(self.user)
        self.assertEqual(primary.company, other)

    def test_deactivate_member(self):
        create_member(self.user, self.company)
        CompanyMember.objects.deactivate_member(self.user, self.company)
        self.assertEqual(
            CompanyMember.objects.for_user(self.user).count(),
            0,
        )


class CompanyMemberViewSetTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="owner", email="owner@example.com")
        self.company = create_company(name="Owner Corp")
        create_member(self.user, self.company)
        self.list_url = reverse("companymember-list")
        self.switch_url = reverse("companymember-switch-company")

    def test_requires_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_sees_only_own_memberships(self):
        other = create_user(username="stranger", email="stranger@example.com")
        other_company = create_company(name="Stranger Corp")
        create_member(other, other_company)
        authenticate(self.client, self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["company"], self.company.id)

    def test_switch_company_sets_primary(self):
        other_company = create_company(name="Second Corp")
        create_member(self.user, other_company, is_primary=False)
        authenticate(self.client, self.user)
        response = self.client.post(
            self.switch_url,
            {"company_id": other_company.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        primary = CompanyMember.objects.primary_for_user(self.user)
        self.assertEqual(primary.company, other_company)

    def test_switch_company_rejects_non_member(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            self.switch_url,
            {"company_id": 99999},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_current_membership_endpoint(self):
        self.client.login(email=self.user.email, password="Password@123")
        response = self.client.get(reverse("companymember-current-membership"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["company"], self.company.id)

    def test_company_admin_can_add_another_user_as_member(self):
        new_user = create_user(username="newhire", email="newhire@example.com")
        role = CompanyMember.objects.get(user=self.user, company=self.company).role
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {
                "user": new_user.id,
                "company": self.company.id,
                "role": role.id,
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], new_user.id)

    def test_regular_user_cannot_add_other_users(self):
        plain = create_user(username="plain", email="plain@example.com")
        new_user = create_user(username="newhire2", email="newhire2@example.com")
        role = CompanyMember.objects.get(user=self.user, company=self.company).role
        authenticate(self.client, plain)
        response = self.client.post(
            self.list_url,
            {
                "user": new_user.id,
                "company": self.company.id,
                "role": role.id,
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], plain.id)


class UserInvitationTests(APITestCase):
    def setUp(self):
        self.admin = create_user(username="invadmin", email="invadmin@example.com")
        self.company = create_company(name="Invite Corp")
        create_member(self.admin, self.company, role_key="company_admin")
        self.invite_url = reverse("companymember-invite")
        self.invitations_url = reverse("companymember-invitations")
        self.accept_url = reverse("companymember-accept-invitation")

    def _invite_payload(self, email, role):
        return {"email": email, "role": role.id}

    def test_requires_authentication(self):
        response = self.client.post(
            self.invite_url,
            {"email": "x@example.com", "role": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manager_can_invite(self):
        authenticate(self.client, self.admin)
        role = get_role("business_analyst")
        response = self.client.post(
            self.invite_url,
            self._invite_payload("invitee@example.com", role),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "pending")
        self.assertIn("token", response.data)
        self.assertTrue(
            UserInvitation.objects.filter(
                company=self.company,
                email="invitee@example.com",
            ).exists()
        )

    def test_non_manager_cannot_invite(self):
        plain = create_user(username="plaininv", email="plaininv@example.com")
        create_member(plain, self.company, role_key="business_analyst")
        authenticate(self.client, plain)
        role = get_role("business_analyst")
        response = self.client.post(
            self.invite_url,
            self._invite_payload("invitee@example.com", role),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_duplicate_pending_invite_rejected(self):
        authenticate(self.client, self.admin)
        role = get_role("business_analyst")
        payload = self._invite_payload("dup@example.com", role)
        first = self.client.post(self.invite_url, payload, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        second = self.client.post(self.invite_url, payload, format="json")
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inviting_existing_user_rejected(self):
        authenticate(self.client, self.admin)
        create_user(username="existing", email="existing@example.com")
        role = get_role("business_analyst")
        response = self.client.post(
            self.invite_url,
            self._invite_payload("existing@example.com", role),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_lists_invitations(self):
        authenticate(self.client, self.admin)
        role = get_role("business_analyst")
        self.client.post(
            self.invite_url,
            self._invite_payload("listme@example.com", role),
            format="json",
        )
        response = self.client.get(self.invitations_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["email"], "listme@example.com")

    def test_non_manager_cannot_list_invitations(self):
        plain = create_user(username="plaininv2", email="plaininv2@example.com")
        create_member(plain, self.company, role_key="business_analyst")
        authenticate(self.client, plain)
        response = self.client.get(self.invitations_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accept_invitation_creates_user_and_membership(self):
        authenticate(self.client, self.admin)
        role = get_role("business_analyst")
        invite_resp = self.client.post(
            self.invite_url,
            self._invite_payload("accept@example.com", role),
            format="json",
        )
        token = invite_resp.data["token"]

        self.client.credentials()
        response = self.client.post(
            self.accept_url,
            {
                "token": token,
                "first_name": "Accept",
                "last_name": "User",
                "password": "InvitePass@123",
                "confirm_password": "InvitePass@123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        user = get_user_model().objects.get(email="accept@example.com")
        self.assertTrue(user.is_active)
        self.assertTrue(
            CompanyMember.objects.filter(
                user=user,
                company=self.company,
                role=role,
            ).exists()
        )
        invitation = UserInvitation.objects.get(token=token)
        self.assertEqual(invitation.status, "accepted")
        self.assertIsNotNone(invitation.accepted_at)

    def test_accept_invitation_rejects_bad_token(self):
        response = self.client.post(
            self.accept_url,
            {
                "token": "not-a-real-token",
                "first_name": "A",
                "last_name": "B",
                "password": "InvitePass@123",
                "confirm_password": "InvitePass@123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_invitation_rejects_password_mismatch(self):
        authenticate(self.client, self.admin)
        role = get_role("business_analyst")
        invite_resp = self.client.post(
            self.invite_url,
            self._invite_payload("mismatch@example.com", role),
            format="json",
        )
        self.client.credentials()
        response = self.client.post(
            self.accept_url,
            {
                "token": invite_resp.data["token"],
                "first_name": "A",
                "last_name": "B",
                "password": "InvitePass@123",
                "confirm_password": "Different@123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_accept_expired_invitation_rejected(self):
        authenticate(self.client, self.admin)
        role = get_role("business_analyst")
        invite_resp = self.client.post(
            self.invite_url,
            self._invite_payload("expire@example.com", role),
            format="json",
        )
        invitation = UserInvitation.objects.get(token=invite_resp.data["token"])
        invitation.expires_at = timezone.now() - timedelta(minutes=1)
        invitation.save(update_fields=["expires_at"])

        self.client.credentials()
        response = self.client.post(
            self.accept_url,
            {
                "token": invitation.token,
                "first_name": "A",
                "last_name": "B",
                "password": "InvitePass@123",
                "confirm_password": "InvitePass@123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, "expired")

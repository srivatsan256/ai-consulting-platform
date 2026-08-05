from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from company_members.models import CompanyMember
from core.tests_helpers import (
    authenticate,
    create_company,
    create_member,
    create_user,
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
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["company"], self.company.id)

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

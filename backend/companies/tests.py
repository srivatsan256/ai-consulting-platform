from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from companies.models import Company
from core.tests_helpers import (
    authenticate,
    create_company,
    create_member,
    create_user,
)


class CompanyModelTests(APITestCase):
    def test_company_name_is_unique(self):
        create_company(name="Unique Corp")
        with self.assertRaises(Exception):
            create_company(name="Unique Corp")

    def test_default_is_active(self):
        company = create_company(name="Active Co")
        self.assertTrue(company.is_active)

    def test_string_representation(self):
        company = create_company(name="Brand Co")
        self.assertEqual(str(company), "Brand Co")

    def test_suspend_syncs_is_active(self):
        company = create_company(name="Suspend Co")
        company.status = "suspended"
        company.save()
        company.refresh_from_db()
        self.assertFalse(company.is_active)
        self.assertTrue(company.is_suspended)


class CompanyViewSetTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="company_user", email="cuser@example.com")
        self.list_url = reverse("company-list")

    def test_requires_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_company(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {
                "company_name": "New Ventures",
                "industry": "Finance",
                "website": "https://example.com",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Company.objects.filter(company_name="New Ventures").exists()
        )

    def test_company_name_is_required(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {"industry": "Finance"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_company(self):
        company = create_company(name="Retrievable Co")
        create_member(self.user, company)
        authenticate(self.client, self.user)
        response = self.client.get(
            reverse("company-detail", args=[company.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["company_name"], "Retrievable Co")

    def test_cannot_retrieve_unrelated_company(self):
        company = create_company(name="Foreign Co")
        other = create_company(name="My Co")
        create_member(self.user, other)
        authenticate(self.client, self.user)
        response = self.client.get(
            reverse("company-detail", args=[company.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_company(self):
        company = create_company(name="Old Name")
        create_member(self.user, company)
        authenticate(self.client, self.user)
        response = self.client.patch(
            reverse("company-detail", args=[company.pk]),
            {"company_name": "New Name"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        company.refresh_from_db()
        self.assertEqual(company.company_name, "New Name")

    def test_delete_company(self):
        company = create_company(name="Doomed Co")
        create_member(self.user, company)
        authenticate(self.client, self.user)
        response = self.client.delete(
            reverse("company-detail", args=[company.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Company.objects.filter(pk=company.pk).exists())

    def test_search_by_name(self):
        my_company = create_company(name="Alpha Ltd")
        create_member(self.user, my_company)
        create_company(name="Beta Inc")
        authenticate(self.client, self.user)
        response = self.client.get(self.list_url, {"search": "Alpha"})
        names = [c["company_name"] for c in response.data]
        self.assertIn("Alpha Ltd", names)
        self.assertNotIn("Beta Inc", names)

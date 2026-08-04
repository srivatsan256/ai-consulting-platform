from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.tests_helpers import authenticate, create_user, get_role
from roles.models import Role


class RoleModelTests(APITestCase):
    def test_role_key_is_unique(self):
        get_role(role_key="company_admin", display_name="Company Admin")
        with self.assertRaises(Exception):
            Role.objects.create(
                role_key="company_admin",
                display_name="Duplicate",
            )

    def test_known_roles_can_be_created(self):
        for key, display in Role.ROLE_CHOICES:
            role = Role.objects.create(
                role_key=key,
                display_name=display,
            )
            self.assertEqual(role.role_key, key)

    def test_string_representation(self):
        role = get_role(role_key="qa_test_engineer", display_name="QA")
        self.assertEqual(str(role), "QA")


class RoleViewSetTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="role_user", email="role@example.com")
        self.list_url = reverse("role-list")

    def test_requires_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_list_roles(self):
        authenticate(self.client, self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_role(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {
                "role_key": "company_admin",
                "display_name": "Company Admin",
                "description": "Manages the tenant",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Role.objects.filter(role_key="company_admin").exists()
        )

    def test_invalid_role_key_rejected(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {
                "role_key": "not_a_real_role",
                "display_name": "Bogus",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_role(self):
        role = get_role()
        authenticate(self.client, self.user)
        response = self.client.get(
            reverse("role-detail", args=[role.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role_key"], "company_admin")

    def test_update_role(self):
        role = get_role()
        authenticate(self.client, self.user)
        response = self.client.patch(
            reverse("role-detail", args=[role.pk]),
            {"description": "Updated description"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        role.refresh_from_db()
        self.assertEqual(role.description, "Updated description")

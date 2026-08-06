from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.tests_helpers import authenticate, create_user, get_role
from permissions.models import Permission


class PermissionModelTests(APITestCase):
    def setUp(self):
        self.role = get_role()

    def test_unique_role_feature_pair(self):
        Permission.objects.create(
            role=self.role,
            feature="dashboard",
            can_view=True,
        )
        with self.assertRaises(Exception):
            Permission.objects.create(
                role=self.role,
                feature="dashboard",
                can_view=True,
            )

    def test_string_representation(self):
        permission = Permission.objects.create(
            role=self.role,
            feature="reports",
            can_view=True,
        )
        self.assertEqual(
            str(permission),
            "Company Admin - reports",
        )


class PermissionViewSetTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="perm_user", email="perm@example.com")
        self.role = get_role()
        self.list_url = reverse("permission-list")

    def test_requires_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_permission(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {
                "role": self.role.id,
                "feature": "project_management",
                "can_view": True,
                "can_create": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Permission.objects.filter(
                role=self.role,
                feature="project_management",
            ).exists()
        )

    def test_duplicate_role_feature_is_rejected(self):
        Permission.objects.create(
            role=self.role,
            feature="dashboard",
            can_view=True,
        )
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {
                "role": self.role.id,
                "feature": "dashboard",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_returns_permissions(self):
        Permission.objects.create(
            role=self.role,
            feature="audit_logs",
            can_view=True,
        )
        authenticate(self.client, self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

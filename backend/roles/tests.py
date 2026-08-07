from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.tests_helpers import (
    authenticate,
    create_company,
    create_member,
    create_user,
    get_role,
)
from roles.models import Role, RoleAssignment


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


class RoleAssignmentEndpointTests(APITestCase):
    def setUp(self):
        self.company = create_company(name="Role Assignment Corp")
        self.admin = create_user(username="ra_admin", email="ra_admin@example.com")
        create_member(self.admin, self.company, role_key="company_admin")
        self.manager = create_user(username="ra_manager", email="ra_manager@example.com")
        create_member(self.manager, self.company, role_key="project_manager")
        self.target = create_user(username="ra_target", email="ra_target@example.com")
        create_member(self.target, self.company, role_key="business_analyst")
        self.admin_role = get_role("company_admin", "Company Admin")
        self.manager_role = get_role("project_manager", "Project Manager")

    def test_admin_can_assign_role(self):
        authenticate(self.client, self.admin)
        response = self.client.post(
            reverse("role-assign"),
            {"user": self.target.id, "role": self.manager_role.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.target.company_memberships.first().refresh_from_db()
        self.assertEqual(
            self.target.company_memberships.first().role.role_key,
            "project_manager",
        )
        self.assertTrue(
            RoleAssignment.objects.filter(
                user=self.target,
                company=self.company,
                role=self.manager_role,
                assigned_by=self.admin,
            ).exists()
        )

    def test_reassign_is_idempotent(self):
        authenticate(self.client, self.admin)
        payload = {"user": self.target.id, "role": self.admin_role.id}
        response = self.client.post(
            reverse("role-assign"),
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(
            reverse("role-assign"),
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_manager_cannot_assign(self):
        authenticate(self.client, self.manager)
        response = self.client.post(
            reverse("role-assign"),
            {"user": self.target.id, "role": self.admin_role.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_change_own_role(self):
        authenticate(self.client, self.admin)
        response = self.client.post(
            reverse("role-assign"),
            {"user": self.admin.id, "role": self.manager_role.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_assign_inactive_role(self):
        inactive = get_role("document_reviewer", "Reviewer")
        inactive.is_active = False
        inactive.save()
        authenticate(self.client, self.admin)
        response = self.client.post(
            reverse("role-assign"),
            {"user": self.target.id, "role": inactive.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_assign_to_non_member(self):
        outsider = create_user(username="ra_outsider", email="ra_outsider@example.com")
        authenticate(self.client, self.admin)
        response = self.client.post(
            reverse("role-assign"),
            {"user": outsider.id, "role": self.admin_role.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mine_returns_role_and_permissions(self):
        authenticate(self.client, self.admin)
        response = self.client.get(reverse("role-mine"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role_key"], "company_admin")

    def test_assignments_history_gated_to_managers(self):
        authenticate(self.client, self.admin)
        self.client.post(
            reverse("role-assign"),
            {"user": self.target.id, "role": self.manager_role.id},
            format="json",
        )
        response = self.client.get(reverse("role-assignments"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

        self.client.force_authenticate(user=None)
        authenticate(self.client, self.manager)
        response = self.client.get(reverse("role-assignments"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from company_members.models import CompanyMember
from roles.models import Role

from authentication.serializers import RegisterSerializer


User = get_user_model()


class RegisterAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("authentication:register")

    def _payload(self, **overrides):
        payload = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "password": "StrongPass@123",
            "confirm_password": "StrongPass@123",
            "account_type": "consultant",
        }
        payload.update(overrides)
        return payload

    def test_consultant_default_role_is_company_admin(self):
        response = self.client.post(self.url, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"]["key"], "company_admin")

    def test_consultant_can_submit_employee_role(self):
        response = self.client.post(
            self.url,
            self._payload(role="project_manager"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"]["key"], "project_manager")
        self.assertEqual(response.data["role"]["name"], "Project Manager")

        user = User.objects.get(email="jane.doe@example.com")
        membership = user.company_memberships.first() # pyright: ignore[reportAttributeAccessIssue]
        self.assertEqual(membership.role.role_key, "project_manager")

    def test_invalid_role_key_is_rejected(self):
        response = self.client.post(
            self.url,
            self._payload(role="not_a_real_role"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("role", response.data.get("errors", {}))
        self.assertFalse(User.objects.filter(email="jane.doe@example.com").exists())

    def test_client_registration_ignores_role(self):
        response = self.client.post(
            self.url,
            self._payload(
                account_type="client",
                company_name="Acme Corp",
                role="backend_developer",
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"]["key"], "client_admin")

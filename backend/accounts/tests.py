from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from company_members.models import CompanyMember
from core.tests_helpers import (
    authenticate,
    create_company,
    create_member,
    create_superuser,
    create_user,
)

User = get_user_model()


class UserModelTests(APITestCase):
    def test_email_is_the_username_field(self):
        self.assertEqual(User.USERNAME_FIELD, "email")

    def test_email_is_unique(self):
        create_user(username="first", email="dup@example.com")
        with self.assertRaises(Exception):
            create_user(username="second", email="dup@example.com")

    def test_password_change_bumps_version_and_timestamp(self):
        user = create_user()
        initial_version = user.password_version
        user.set_password("NewPassword@456")
        self.assertEqual(user.password_version, initial_version + 1)
        self.assertIsNotNone(user.password_changed_at)

    def test_password_changed_at_set_on_creation(self):
        user = create_user()
        self.assertIsNotNone(user.password_changed_at)


class UserViewSetTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="viewer", email="viewer@example.com")
        self.company = create_company(name="Viewer Corp")
        create_member(
            self.user,
            self.company,
            role_key="business_analyst",
            is_primary=True,
        )
        self.list_url = reverse("user-list")

    def _manager(self):
        admin = create_user(username="admin", email="admin@example.com")
        company = create_company(name="Admin Corp")
        create_member(admin, company, role_key="company_admin")
        return admin, company

    def test_requires_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_list(self):
        authenticate(self.client, self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_can_retrieve_detail(self):
        authenticate(self.client, self.user)
        response = self.client.get(reverse("user-detail", args=[self.user.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_authenticated_user_cannot_retrieve_foreign_user(self):
        foreign = create_user(username="foreign", email="foreign@example.com")
        other_company = create_company(name="Other Corp")
        create_member(
            foreign,
            other_company,
            role_key="business_analyst",
            is_primary=True,
        )
        authenticate(self.client, self.user)
        response = self.client.get(reverse("user-detail", args=[foreign.pk]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_user(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {
                "username": "newbie",
                "email": "newbie@example.com",
                "password": "Password@123",
                "first_name": "New",
                "last_name": "User",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(email="newbie@example.com").exists()
        )

    def test_update_user(self):
        authenticate(self.client, self.user)
        response = self.client.patch(
            reverse("user-detail", args=[self.user.pk]),
            {"first_name": "Updated"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")

    def test_search_filters_users(self):
        other_company = create_company(name="Other Corp")
        create_member(
            create_user(username="other", email="other@example.com"),
            other_company,
            role_key="business_analyst",
            is_primary=True,
        )
        authenticate(self.client, self.user)
        response = self.client.get(
            self.list_url,
            {"search": self.user.email},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        emails = [u["email"] for u in response.data["results"]]
        self.assertIn(self.user.email, emails)
        self.assertNotIn("other@example.com", emails)

    def test_superuser_can_delete_user(self):
        admin = create_superuser()
        target = create_user(username="goner", email="goner@example.com")
        authenticate(self.client, admin)
        response = self.client.delete(reverse("user-detail", args=[target.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            User.objects.filter(pk=target.pk).exists()
        )

    def test_deactivate_user(self):
        admin, company = self._manager()
        authenticate(self.client, admin)
        target = create_user(username="deact", email="deact@example.com")
        membership = create_member(
            target,
            company,
            role_key="business_analyst",
            is_primary=False,
        )
        response = self.client.post(
            reverse("user-deactivate", args=[target.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        membership.refresh_from_db()
        self.assertFalse(target.is_active)
        self.assertFalse(membership.is_active)

    def test_activate_user(self):
        admin, company = self._manager()
        authenticate(self.client, admin)
        target = create_user(username="inactive", email="inactive@example.com")
        target.is_active = False
        target.save(update_fields=["is_active"])
        membership = create_member(
            target,
            company,
            role_key="business_analyst",
            is_primary=False,
        )
        membership.is_active = False
        membership.save(update_fields=["is_active"])
        response = self.client.post(
            reverse("user-activate", args=[target.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        membership.refresh_from_db()
        self.assertTrue(target.is_active)
        self.assertTrue(membership.is_active)

    def test_cannot_deactivate_self(self):
        admin, _ = self._manager()
        authenticate(self.client, admin)
        response = self.client.post(
            reverse("user-deactivate", args=[admin.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        admin.refresh_from_db()
        self.assertTrue(admin.is_active)

    def test_non_manager_cannot_deactivate(self):
        plain = create_user(username="plain", email="plain@example.com")
        company = create_company(name="Plain Corp")
        create_member(plain, company, role_key="business_analyst")
        authenticate(self.client, plain)
        target = create_user(username="deact2", email="deact2@example.com")
        create_member(
            target,
            company,
            role_key="business_analyst",
            is_primary=False,
        )
        response = self.client.post(
            reverse("user-deactivate", args=[target.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        target.refresh_from_db()
        self.assertTrue(target.is_active)

    def test_non_manager_cannot_activate(self):
        plain = create_user(username="plain2", email="plain2@example.com")
        company = create_company(name="Plain Corp 2")
        create_member(plain, company, role_key="business_analyst")
        authenticate(self.client, plain)
        target = create_user(username="inactive2", email="inactive2@example.com")
        create_member(
            target,
            company,
            role_key="business_analyst",
            is_primary=False,
        )
        target.is_active = False
        target.save(update_fields=["is_active"])
        response = self.client.post(
            reverse("user-activate", args=[target.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bulk_import_creates_users(self):
        admin, company = self._manager()
        authenticate(self.client, admin)
        response = self.client.post(
            reverse("user-bulk-import"),
            {
                "users": [
                    {
                        "email": "import1@example.com",
                        "first_name": "Imp",
                        "last_name": "One",
                        "role": "business_analyst",
                    },
                    {
                        "email": "import2@example.com",
                        "first_name": "Imp",
                        "last_name": "Two",
                    },
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["created"]), 2)
        user = User.objects.get(email="import1@example.com")
        self.assertTrue(
            CompanyMember.objects.filter(
                user=user,
                company=company,
            ).exists()
        )

    def test_bulk_import_from_csv(self):
        admin, _ = self._manager()
        authenticate(self.client, admin)
        csv_bytes = (
            "email,first_name,last_name,role\n"
            "csv1@example.com,CSV,One,business_analyst\n"
        ).encode()
        response = self.client.post(
            reverse("user-bulk-import"),
            {"file": SimpleUploadedFile("users.csv", csv_bytes)},
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["created"]), 1)
        self.assertTrue(
            User.objects.filter(email="csv1@example.com").exists()
        )

    def test_bulk_import_skips_existing_user(self):
        admin, company = self._manager()
        authenticate(self.client, admin)
        existing = create_user(username="exists", email="exists@example.com")
        response = self.client.post(
            reverse("user-bulk-import"),
            {"users": [{"email": "exists@example.com"}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["skipped"]), 1)
        self.assertTrue(
            CompanyMember.objects.filter(
                user=existing,
                company=company,
            ).exists()
        )

    def test_bulk_import_requires_manager(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            reverse("user-bulk-import"),
            {"users": [{"email": "x@example.com"}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bulk_import_reports_row_errors(self):
        admin, _ = self._manager()
        authenticate(self.client, admin)
        response = self.client.post(
            reverse("user-bulk-import"),
            {"users": [{"first_name": "NoEmail"}, {"email": ""}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["errors"]), 2)

    def test_export_users_csv(self):
        admin, company = self._manager()
        create_member(
            create_user(username="extra", email="extra@example.com"),
            company,
            role_key="business_analyst",
            is_primary=False,
        )
        authenticate(self.client, admin)
        response = self.client.get(reverse("user-export"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv")
        content = response.content.decode()
        self.assertIn("email,username,first_name", content)
        self.assertIn(admin.email, content)
        self.assertIn("extra@example.com", content)

    def test_export_requires_manager(self):
        authenticate(self.client, self.user)
        response = self.client.get(reverse("user-export"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

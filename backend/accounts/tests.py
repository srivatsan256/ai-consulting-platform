from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.tests_helpers import authenticate, create_superuser, create_user

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
        self.list_url = reverse("user-list")

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
        create_user(username="other", email="other@example.com")
        authenticate(self.client, self.user)
        response = self.client.get(
            self.list_url,
            {"search": self.user.email},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        emails = [u["email"] for u in response.data]
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

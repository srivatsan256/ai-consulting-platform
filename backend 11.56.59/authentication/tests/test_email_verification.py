from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class EmailVerificationTests(APITestCase):
    """
    Tests for Email Verification APIs.
    """

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="john",
            email="john@example.com",
            password="Password@123",
            is_email_verified=False,
        )

        self.request_url = reverse(
            "authentication:email-verification-request"
        )

    def test_request_verification_email(self) -> None:
        """
        Existing user should receive verification email.
        """

        response = self.client.post(
            self.request_url,
            {
                "email": self.user.email,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(response.data["success"])

    def test_request_unknown_email(self) -> None:
        """
        Unknown email should return the same response.
        """

        response = self.client.post(
            self.request_url,
            {
                "email": "unknown@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(response.data["success"])
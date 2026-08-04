import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import PasswordResetOtp


User = get_user_model()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class PasswordResetOtpTests(APITestCase):
    """
    Tests for the OTP-based password reset flow.
    """

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="john",
            email="john@example.com",
            password="Password@123",
        )

        self.request_url = reverse(
            "authentication:password-reset-request"
        )
        self.verify_url = reverse(
            "authentication:password-reset-verify-otp"
        )
        self.confirm_url = reverse(
            "authentication:password-reset-confirm"
        )

    def _request_otp(self, email: str | None = None) -> None:
        """POST the request endpoint for the given email."""
        response = self.client.post(
            self.request_url,
            {"email": email or self.user.email},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        return response

    def _extract_otp(self) -> str:
        """Return the 6-digit OTP from the last sent email."""
        email = mail.outbox[-1]
        match = re.search(r"\b(\d{6})\b", email.body)
        self.assertIsNotNone(match, "No OTP found in email body")
        return match.group(1)

    def _verify_otp(self, otp: str, email: str | None = None):
        return self.client.post(
            self.verify_url,
            {
                "email": email or self.user.email,
                "otp": otp,
            },
            format="json",
        )

    def test_full_reset_flow(self) -> None:
        """
        Request -> verify -> confirm should change the password.
        """
        self._request_otp()
        otp = self._extract_otp()

        verify_response = self._verify_otp(otp)
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.assertTrue(verify_response.data["success"])
        uid = verify_response.data["data"]["uid"]
        token = verify_response.data["data"]["token"]

        confirm_response = self.client.post(
            self.confirm_url,
            {
                "uid": uid,
                "token": token,
                "new_password": "NewPassword@789",
                "confirm_password": "NewPassword@789",
            },
            format="json",
        )
        self.assertEqual(
            confirm_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertTrue(confirm_response.data["success"])

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPassword@789"))

    def test_request_sends_otp_email(self) -> None:
        """
        Requesting a reset should email a 6-digit OTP.
        """
        self._request_otp()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        otp = self._extract_otp()
        self.assertTrue(otp.isdigit())
        self.assertEqual(len(otp), 6)

    def test_request_unknown_email_returns_same_response(self) -> None:
        """
        Unknown emails should not reveal that no account exists.
        """
        self._request_otp("unknown@example.com")
        self.assertEqual(len(mail.outbox), 0)

    def test_verify_wrong_otp_rejected(self) -> None:
        """
        An incorrect OTP should be rejected.
        """
        self._request_otp()
        otp = self._extract_otp()

        wrong = "000000" if otp != "000000" else "111111"
        response = self._verify_otp(wrong)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_verify_used_otp_rejected(self) -> None:
        """
        A successfully verified OTP cannot be reused.
        """
        self._request_otp()
        otp = self._extract_otp()

        first = self._verify_otp(otp)
        self.assertEqual(first.status_code, status.HTTP_200_OK)

        second = self._verify_otp(otp)
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_expired_otp_rejected(self) -> None:
        """
        An expired OTP should be rejected.
        """
        self._request_otp()
        otp = self._extract_otp()

        record = PasswordResetOtp.objects.get(email=self.user.email)
        record.expires_at = timezone.now() - timezone.timedelta(minutes=1)
        record.save(update_fields=["expires_at"])

        response = self._verify_otp(otp)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_new_request_invalidates_previous_otp(self) -> None:
        """
        Requesting a new OTP should invalidate the previous one.
        """
        self._request_otp()
        old_otp = self._extract_otp()

        self._request_otp()

        response = self._verify_otp(old_otp)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_rejects_non_digit_otp(self) -> None:
        """
        The serializer should reject non-numeric OTP values.
        """
        self._request_otp()

        response = self._verify_otp("abcdef")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

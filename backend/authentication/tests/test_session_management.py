from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore

from companies.models import Company
from company_members.models import CompanyMember
from roles.models import Role


User = get_user_model()


def create_company(name="Acme Corp"):
    return Company.objects.create(
        company_name=name,
        industry="Technology",
    )


def create_role():
    return Role.objects.get_or_create(
        role_key="company_admin",
        defaults={"display_name": "Company Admin"},
    )[0]


def create_member(user, company, is_primary=True):
    role = create_role()
    return CompanyMember.objects.create(
        user=user,
        company=company,
        role=role,
        is_primary=is_primary,
    )


class SessionManagementTests(APITestCase):
    """
    Tests for session creation, revocation and JWT invalidation.
    """

    def setUp(self):
        self.password = "OldPassword@123"
        self.user = User.objects.create_user(
            username="session_probe",
            email="session_probe@example.com",
            password=self.password,
        )
        self.company = create_company()
        self.membership = create_member(self.user, self.company)

        self.login_url = reverse("authentication:login")
        self.refresh_url = reverse("authentication:token_refresh")
        self.logout_url = reverse("authentication:logout")
        self.me_url = reverse("authentication:current_user")
        self.change_password_url = reverse("authentication:change_password")

    def _login(self):
        response = self.client.post(
            self.login_url,
            {"email": self.user.email, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data.get("data", response.data)

    def test_session_service_is_importable(self):
        """
        Bug C regression: SessionService must import cleanly.
        """
        from authentication.services.session_service import SessionService

        self.assertTrue(SessionService)

    def test_login_creates_user_session_and_login_history(self):
        from authentication.models import LoginHistory, UserSession

        self._login()

        session = UserSession.objects.filter(user=self.user).first()
        self.assertIsNotNone(session)
        self.assertTrue(session.is_active)
        self.assertIsNotNone(session.refresh_token_jti)
        self.assertEqual(session.company, self.company)

        login_history = LoginHistory.objects.filter(user=self.user)
        self.assertEqual(login_history.count(), 1)
        self.assertEqual(
            login_history.first().event_type,
            LoginHistory.EventType.LOGIN_SUCCESS,
        )

    def test_failed_login_records_failed_event(self):
        from authentication.models import LoginHistory

        response = self.client.post(
            self.login_url,
            {"email": self.user.email, "password": "WrongPassword@123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        event = LoginHistory.objects.filter(
            user=None,
            event_type=LoginHistory.EventType.LOGIN_FAILED,
        ).first()
        self.assertIsNotNone(event)
        self.assertEqual(event.email, self.user.email)

    def test_logout_revokes_session_and_records_logout(self):
        from authentication.models import LoginHistory, UserSession

        tokens = self._login()
        session = UserSession.objects.get(user=self.user)
        self.assertTrue(session.is_active)

        response = self.client.post(
            self.logout_url,
            {"refresh": tokens["refresh"]},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        session.refresh_from_db()
        self.assertFalse(session.is_active)
        self.assertIsNotNone(session.revoked_at)

        logout_event = LoginHistory.objects.filter(
            user=self.user,
            event_type=LoginHistory.EventType.LOGOUT,
        )
        self.assertEqual(logout_event.count(), 1)

    def test_logout_with_invalid_token_returns_400(self):
        tokens = self._login()
        response = self.client.post(
            self.logout_url,
            {"refresh": "not-a-valid-token"},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_missing_token_returns_400(self):
        tokens = self._login()
        response = self.client.post(
            self.logout_url,
            {},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_old_access_token_invalid_after_password_change(self):
        tokens = self._login()

        response = self.client.post(
            self.change_password_url,
            {
                "old_password": self.password,
                "new_password": "NewPassword@456",
                "confirm_password": "NewPassword@456",
            },
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            self.me_url,
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_old_refresh_token_invalid_after_password_change(self):
        tokens = self._login()

        self.client.post(
            self.change_password_url,
            {
                "old_password": self.password,
                "new_password": "NewPassword@456",
                "confirm_password": "NewPassword@456",
            },
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}",
        )

        response = self.client.post(
            self.refresh_url,
            {"refresh": tokens["refresh"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_old_access_token_invalid_after_password_reset(self):
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        from authentication.services.password_reset_service import (
            PasswordResetService,
        )

        tokens = self._login()

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.user.refresh_from_db()
        reset_token = PasswordResetService._token_generator.make_token(
            self.user
        )
        PasswordResetService.reset_password(
            uid=uid,
            token=reset_token,
            new_password="ResetPassword@789",
        )

        response = self.client.get(
            self.me_url,
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_change_revokes_all_sessions(self):
        from authentication.models import UserSession

        tokens = self._login()

        self.client.post(
            self.change_password_url,
            {
                "old_password": self.password,
                "new_password": "NewPassword@456",
                "confirm_password": "NewPassword@456",
            },
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}",
        )

        session = UserSession.objects.get(user=self.user)
        self.assertFalse(session.is_active)

    def test_refresh_rotates_session_jti(self):
        from authentication.models import UserSession

        tokens = self._login()
        session = UserSession.objects.get(user=self.user)
        original_jti = session.refresh_token_jti

        response = self.client.post(
            self.refresh_url,
            {"refresh": tokens["refresh"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data.get("data", {}))

        session.refresh_from_db()
        self.assertNotEqual(session.refresh_token_jti, original_jti)

        # The original refresh token must be blacklisted after rotation.
        replay = self.client.post(
            self.refresh_url,
            {"refresh": tokens["refresh"]},
            format="json",
        )
        self.assertEqual(replay.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_audit_logs_written_for_session_events(self):
        from audit_logs.models import AuditLog

        self._login()

        self.assertTrue(
            AuditLog.objects.filter(
                action="SESSION_CREATED",
                user=self.user,
            ).exists()
        )

    # ------------------------------------------------------------------
    # Concurrent session limit
    # ------------------------------------------------------------------

    def test_concurrent_session_limit_revokes_oldest(self):
        from settings_app.models import SystemSetting

        SystemSetting.set_value(
            "auth.max_concurrent_sessions",
            2,
            category="security",
        )
        from authentication.models import UserSession

        self._login()
        self._login()
        third = self._login()

        active = UserSession.objects.active().filter(
            user=self.user,
            company=self.company,
        )
        self.assertEqual(active.count(), 2)

        third_jti = RefreshToken(third["refresh"])["jti"]
        self.assertTrue(
            active.filter(refresh_token_jti=third_jti).exists(),
            "The newest session must survive enforcement.",
        )

    def test_concurrent_limit_uses_system_setting(self):
        from settings_app.models import SystemSetting

        SystemSetting.set_value(
            "auth.max_concurrent_sessions",
            1,
            category="security",
        )
        from authentication.models import UserSession

        self._login()
        self._login()

        active = UserSession.objects.active().filter(
            user=self.user,
            company=self.company,
        )
        self.assertEqual(active.count(), 1)

    # ------------------------------------------------------------------
    # Session management endpoints
    # ------------------------------------------------------------------

    def _sessions_url(self):
        return reverse("authentication:session-list")

    def _auth_login(self):
        tokens = self._login()
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}"
        )
        return tokens

    def test_sessions_list_requires_authentication(self):
        response = self.client.get(self._sessions_url())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_sessions_list_returns_only_own_active_sessions(self):
        from authentication.models import UserSession

        self._auth_login()
        self._auth_login()

        response = self.client.get(self._sessions_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 2)

        total = UserSession.objects.filter(user=self.user).count()
        self.assertEqual(total, 2)

    def test_sessions_list_does_not_leak_foreign_sessions(self):
        other_user = User.objects.create_user(
            username="other_user",
            email="other_user@example.com",
            password=self.password,
        )
        other_company = create_company(name="Other Corp")
        create_member(other_user, other_company)

        self.client.post(
            self.login_url,
            {"email": other_user.email, "password": self.password},
            format="json",
        )

        self._auth_login()
        response = self.client.get(self._sessions_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 1)

    def test_revoke_single_session(self):
        from authentication.models import UserSession

        first = self._login()
        second = self._login()

        first_jti = RefreshToken(first["refresh"])["jti"]
        target = UserSession.objects.get(refresh_token_jti=first_jti)

        response = self.client.post(
            reverse("authentication:session-revoke", args=[target.id]),
            {},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {second['access']}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        target.refresh_from_db()
        self.assertFalse(target.is_active)
        self.assertIsNotNone(target.revoked_at)

        other = UserSession.objects.get(
            refresh_token_jti=RefreshToken(second["refresh"])["jti"]
        )
        self.assertTrue(other.is_active)

    def test_revoke_current_session_rejected(self):
        from authentication.models import UserSession

        tokens = self._login()
        session = UserSession.objects.get(user=self.user)

        response = self.client.post(
            reverse("authentication:session-revoke", args=[session.id]),
            {},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}",
            HTTP_X_SESSION_REFRESH=tokens["refresh"],
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        session.refresh_from_db()
        self.assertTrue(session.is_active)

    def test_revoke_foreign_session_hidden(self):
        from authentication.models import UserSession

        other_user = User.objects.create_user(
            username="other2",
            email="other2@example.com",
            password=self.password,
        )
        other_company = create_company(name="Other Corp 2")
        create_member(other_user, other_company)

        self.client.post(
            self.login_url,
            {"email": other_user.email, "password": self.password},
            format="json",
        )
        foreign = UserSession.objects.get(user=other_user)

        tokens = self._login()
        response = self.client.post(
            reverse("authentication:session-revoke", args=[foreign.id]),
            {},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        foreign.refresh_from_db()
        self.assertTrue(foreign.is_active)

    def test_revoke_all_requires_current_refresh_header(self):
        self._login()
        response = self.client.post(
            reverse("authentication:session-revoke-all"),
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_revoke_all_keeps_current_session(self):
        from authentication.models import UserSession

        first = self._login()
        second = self._login()
        third = self._login()

        first_jti = RefreshToken(first["refresh"])["jti"]
        second_jti = RefreshToken(second["refresh"])["jti"]
        third_jti = RefreshToken(third["refresh"])["jti"]

        response = self.client.post(
            reverse("authentication:session-revoke-all"),
            {},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {third['access']}",
            HTTP_X_SESSION_REFRESH=third["refresh"],
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["revoked"], 2)

        current = UserSession.objects.get(refresh_token_jti=third_jti)
        self.assertTrue(current.is_active)

        first_s = UserSession.objects.get(refresh_token_jti=first_jti)
        second_s = UserSession.objects.get(refresh_token_jti=second_jti)
        self.assertFalse(first_s.is_active)
        self.assertFalse(second_s.is_active)

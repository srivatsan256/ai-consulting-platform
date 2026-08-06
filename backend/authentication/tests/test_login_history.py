from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models.login_history import LoginHistory
from authentication.serializers import LoginHistorySerializer
from companies.models import Company
from company_members.models import CompanyMember
from roles.models import Role

from .test_session_management import create_member


User = get_user_model()


class LoginHistoryServiceTests(APITestCase):
    """
    Tests for LoginHistoryService and the login history API.
    """

    def setUp(self):
        self.password = "Password@123"
        self.user = User.objects.create_user(
            username="history_probe",
            email="history_probe@example.com",
            password=self.password,
        )
        self.company = Company.objects.create(
            company_name="History Corp",
            industry="Consulting",
        )
        self.membership = create_member(self.user, self.company)

        self.login_url = reverse("authentication:login")
        self.history_url = reverse("authentication:login-history-list")

    def test_login_history_service_is_importable(self):
        """
        Regression: LoginEventType import previously broke the module.
        """
        from authentication.services.login_history import (
            LoginEventType,
            LoginHistoryService,
        )

        self.assertTrue(LoginEventType)
        self.assertTrue(LoginHistoryService)

    def test_login_success_is_scoped_to_company(self):
        self.client.post(
            self.login_url,
            {"email": self.user.email, "password": self.password},
            format="json",
        )

        event = LoginHistory.objects.filter(
            user=self.user,
            event_type=LoginHistory.EventType.LOGIN_SUCCESS,
        ).first()
        self.assertIsNotNone(event)
        self.assertEqual(event.company, self.company)

    def test_serializer_returns_company_name(self):
        event = LoginHistory.objects.create(
            user=self.user,
            company=self.company,
            event_type=LoginHistory.EventType.LOGIN_SUCCESS,
        )

        data = LoginHistorySerializer(event).data
        self.assertEqual(data["company_name"], self.company.company_name)

    def test_login_history_list_returns_records_for_superuser(self):
        LoginHistory.objects.create(
            user=self.user,
            company=self.company,
            event_type=LoginHistory.EventType.LOGIN_SUCCESS,
            ip_address="127.0.0.1",
        )

        admin = User.objects.create_superuser(
            username="root",
            email="root@example.com",
            password="AdminPass@123",
        )

        self.client.force_authenticate(admin)
        response = self.client.get(self.history_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], True)

    def test_login_history_list_scoped_to_tenant(self):
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="Password@123",
        )
        other_company = Company.objects.create(
            company_name="Other Corp",
            industry="Finance",
        )
        create_member(other_user, other_company)

        LoginHistory.objects.create(
            user=self.user,
            company=self.company,
            event_type=LoginHistory.EventType.LOGIN_SUCCESS,
        )
        LoginHistory.objects.create(
            user=other_user,
            company=other_company,
            event_type=LoginHistory.EventType.LOGIN_SUCCESS,
        )

        content_type = ContentType.objects.get_for_model(LoginHistory)
        permission = Permission.objects.get(
            codename="view_loginhistory",
            content_type=content_type,
        )
        self.user.user_permissions.add(permission)

        self.client.force_authenticate(self.user)
        response = self.client.get(self.history_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        records = response.data["data"]["results"]
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["company"], self.company.id)

from rest_framework import status
from rest_framework.test import APITestCase

from core.tests_helpers import (
    authenticate,
    create_company,
    create_member,
    create_superuser,
    create_user,
)
from settings_app.models import Announcement, SystemSetting


class SystemSettingTests(APITestCase):
    def test_get_value_default(self):
        self.assertIsNone(SystemSetting.get_value("missing", None))

    def test_get_value_typed_default(self):
        self.assertFalse(SystemSetting.get_value("maintenance_mode", False))

    def test_set_value_roundtrip(self):
        SystemSetting.set_value("maintenance_mode", "true", category="security")
        self.assertTrue(SystemSetting.get_value("maintenance_mode", False))

    def test_get_value_cast_to_int(self):
        SystemSetting.set_value("page_size", "50")
        self.assertEqual(SystemSetting.get_value("page_size", 20), 50)


class AnnouncementTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="announcer", email="ann@example.com")
        self.company = create_company(name="Announce Corp")
        create_member(self.user, self.company)
        self.list_url = "/api/settings/announcements/"

    def test_requires_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_tenant_announcement(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {
                "title": "Server maintenance",
                "message": "Downtime this weekend.",
                "scope": "tenant",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        announcement = Announcement.objects.get(title="Server maintenance")
        self.assertEqual(announcement.company, self.company)
        self.assertEqual(announcement.created_by, self.user)

    def test_tenant_list_only_returns_visible_company_announcements(self):
        other = create_company(name="Other Corp")
        Announcement.objects.create(
            title="Mine",
            message="msg",
            scope="tenant",
            company=self.company,
        )
        Announcement.objects.create(
            title="Theirs",
            message="msg",
            scope="tenant",
            company=other,
        )
        Announcement.objects.create(
            title="Expired",
            message="msg",
            scope="tenant",
            company=self.company,
            is_active=False,
        )
        authenticate(self.client, self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [a["title"] for a in response.data["results"]]
        self.assertIn("Mine", titles)
        self.assertNotIn("Theirs", titles)
        self.assertNotIn("Expired", titles)

    def test_non_staff_cannot_create_global_announcement(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {"title": "Global", "message": "msg", "scope": "global"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_can_create_global_announcement(self):
        admin = create_superuser(username="admin2", email="admin2@example.com")
        authenticate(self.client, admin)
        response = self.client.post(
            self.list_url,
            {"title": "Global", "message": "msg", "scope": "global"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

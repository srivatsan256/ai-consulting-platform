from rest_framework import status
from rest_framework.test import APITestCase

from core.tests_helpers import create_superuser
from settings_app.models import SystemSetting


class HealthCheckTests(APITestCase):
    def test_health_check_unauthenticated(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")
        self.assertEqual(response.data["database"], "ok")

    def test_health_check_reports_version(self):
        response = self.client.get("/api/health/")
        self.assertIn("version", response.data)


class MaintenanceModeTests(APITestCase):
    def setUp(self):
        SystemSetting.set_value("maintenance_mode", "true", category="security")

    def test_maintenance_mode_blocks_api(self):
        response = self.client.get("/api/companies/")
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_health_check_stays_available_in_maintenance(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_superuser_bypasses_maintenance(self):
        admin = create_superuser(username="maint_admin", email="maint@example.com")
        self.client.force_login(admin)
        response = self.client.get("/api/companies/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

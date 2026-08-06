from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase

from core.tests_helpers import authenticate, create_user
from notifications.models import Notification, NotificationPreference
from notifications.services.service import NotificationService


class NotificationServiceTests(TestCase):
    def setUp(self):
        self.user = create_user(username="recipient", email="recipient@example.com")

    def test_notify_creates_notification(self):
        notification = NotificationService.notify(
            recipient=self.user,
            title="Hello",
            message="World",
            category="task",
            entity_type="task",
            entity_id=1,
        )
        self.assertIsNotNone(notification)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.get().recipient, self.user)

    def test_notify_respects_disabled_category_preference(self):
        NotificationPreference.objects.create(
            user=self.user,
            task_notifications=False,
        )
        result = NotificationService.notify(
            recipient=self.user,
            title="Task",
            message="Assigned",
            category="task",
        )
        self.assertIsNone(result)
        self.assertEqual(Notification.objects.count(), 0)

    def test_notify_other_categories_still_created(self):
        NotificationPreference.objects.create(
            user=self.user,
            task_notifications=False,
        )
        NotificationService.notify(
            recipient=self.user,
            title="Review",
            message="Needs review",
            category="review",
        )
        self.assertEqual(Notification.objects.count(), 1)


class NotificationViewSetTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="notifview", email="notifview@example.com")
        authenticate(self.client, self.user)

    def test_create_notification_defaults_recipient_to_request_user(self):
        response = self.client.post(
            "/api/notifications/",
            {
                "title": "Hello",
                "message": "World",
                "notification_type": "info",
                "category": "system",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        notification = Notification.objects.get()
        self.assertEqual(notification.recipient, self.user)

    def test_list_only_returns_own_notifications(self):
        other = create_user(username="notifview2", email="notifview2@example.com")
        Notification.objects.create(
            recipient=self.user, title="Mine", message="x", category="system"
        )
        Notification.objects.create(
            recipient=other, title="Theirs", message="x", category="system"
        )
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [n["title"] for n in response.data["results"]]
        self.assertIn("Mine", titles)
        self.assertNotIn("Theirs", titles)

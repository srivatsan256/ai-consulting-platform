from rest_framework import serializers

from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "title",
            "message",
            "notification_type",
            "category",
            "entity_type",
            "entity_id",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = (
            "id",
            "recipient",
            "read_at",
            "created_at",
        )


class NotificationPreferenceSerializer(serializers.ModelSerializer):

    class Meta:
        model = NotificationPreference
        fields = [
            "id",
            "user",
            "email_notifications",
            "task_notifications",
            "approval_notifications",
            "review_notifications",
            "meeting_notifications",
            "deployment_notifications",
            "system_notifications",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "user",
            "created_at",
            "updated_at",
        )

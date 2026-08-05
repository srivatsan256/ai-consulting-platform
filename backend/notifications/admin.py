from django.contrib import admin

from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "recipient",
        "notification_type",
        "category",
        "is_read",
        "created_at",
    )

    list_filter = (
        "notification_type",
        "category",
        "is_read",
    )

    search_fields = (
        "title",
        "message",
    )


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "email_notifications",
        "task_notifications",
        "approval_notifications",
    )

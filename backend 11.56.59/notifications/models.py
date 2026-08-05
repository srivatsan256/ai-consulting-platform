from django.db import models

from accounts.models import User


class Notification(models.Model):

    class Scope(models.TextChoices):
        TENANT = "tenant"
        GLOBAL = "global"

    NOTIFICATION_TYPE = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("success", "Success"),
        ("error", "Error"),
    ]

    CATEGORY = [
        ("task", "Task"),
        ("approval", "Approval"),
        ("review", "Review"),
        ("meeting", "Meeting"),
        ("deployment", "Deployment"),
        ("system", "System"),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    title = models.CharField(max_length=255)

    message = models.TextField()

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE,
        default="info",
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY,
        default="system",
    )

    scope = models.CharField(
        max_length=10,
        choices=Scope.choices,
        default=Scope.TENANT,
    )

    entity_type = models.CharField(max_length=100, blank=True)

    entity_id = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    is_read = models.BooleanField(default=False)

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} -> {self.recipient}"


class NotificationPreference(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )

    email_notifications = models.BooleanField(default=True)

    task_notifications = models.BooleanField(default=True)

    approval_notifications = models.BooleanField(default=True)

    review_notifications = models.BooleanField(default=True)

    meeting_notifications = models.BooleanField(default=True)

    deployment_notifications = models.BooleanField(default=True)

    system_notifications = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notification_preferences"

    def __str__(self):
        return f"Preferences for {self.user}"

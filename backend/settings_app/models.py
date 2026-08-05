from django.db import models

from accounts.models import User


class SystemSetting(models.Model):

    CATEGORY = [
        ("general", "General"),
        ("security", "Security"),
        ("email", "Email"),
        ("ai", "AI Configuration"),
        ("integration", "Integration"),
        ("notification", "Notification"),
    ]

    key = models.CharField(
        max_length=255,
        unique=True,
    )

    value = models.TextField(blank=True)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY,
        default="general",
    )

    description = models.TextField(blank=True)

    is_sensitive = models.BooleanField(default=False)

    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="settings_updated",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_settings"
        ordering = ["category", "key"]

    def __str__(self):
        return self.key


class UserProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
    )

    bio = models.TextField(blank=True)

    timezone = models.CharField(
        max_length=50,
        default="UTC",
    )

    language = models.CharField(
        max_length=10,
        default="en",
    )

    theme = models.CharField(
        max_length=20,
        default="light",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profiles"

    def __str__(self):
        return f"Profile of {self.user}"

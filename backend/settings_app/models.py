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

    @classmethod
    def get_value(cls, key, default=None):
        """
        Return the stored value for ``key`` cast to the type of ``default``.
        """
        setting = cls.objects.filter(key=key).only("value").first()
        if setting is None:
            return default
        if isinstance(default, bool):
            return str(setting.value).strip().lower() in ("true", "1", "yes", "on")
        if isinstance(default, int):
            try:
                return int(setting.value)
            except (TypeError, ValueError):
                return default
        return setting.value

    @classmethod
    def set_value(cls, key, value, category="general", updated_by=None):
        setting, _ = cls.objects.update_or_create(
            key=key,
            defaults={
                "value": str(value),
                "category": category,
                "updated_by": updated_by,
            },
        )
        return setting


class Announcement(models.Model):

    class Scope(models.TextChoices):
        TENANT = "tenant", "Tenant"
        GLOBAL = "global", "Global"

    LEVEL = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("success", "Success"),
        ("error", "Error"),
    ]

    title = models.CharField(max_length=255)

    message = models.TextField()

    level = models.CharField(
        max_length=20,
        choices=LEVEL,
        default="info",
    )

    scope = models.CharField(
        max_length=10,
        choices=Scope.choices,
        default=Scope.TENANT,
    )

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="announcements",
    )

    is_active = models.BooleanField(default=True)

    scheduled_for = models.DateTimeField(
        null=True,
        blank=True,
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "announcements"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def is_visible(self):
        from django.utils import timezone

        now = timezone.now()
        if not self.is_active:
            return False
        if self.scheduled_for and self.scheduled_for > now:
            return False
        if self.expires_at and self.expires_at < now:
            return False
        return True


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

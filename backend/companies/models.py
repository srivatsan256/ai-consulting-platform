from django.db import models
from django.utils import timezone

from core.validators import validate_hex_color


class CompanyStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    ARCHIVED = "archived", "Archived"


class Company(models.Model):
    company_name = models.CharField(max_length=255, unique=True)
    industry = models.CharField(max_length=150)
    business_description = models.TextField(blank=True)

    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)

    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=CompanyStatus.choices,
        default=CompanyStatus.ACTIVE,
        db_index=True,
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "companies"
        ordering = ["company_name"]

    def __str__(self):
        return self.company_name

    @property
    def is_suspended(self):
        return self.status == CompanyStatus.SUSPENDED

    @property
    def is_archived(self):
        return self.status == CompanyStatus.ARCHIVED

    def save(self, *args, **kwargs):
        self.is_active = self.status == CompanyStatus.ACTIVE
        super().save(*args, **kwargs)


class CompanySettings(models.Model):
    """
    One-to-one settings and branding profile for a tenant company.
    """

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name="settings",
    )

    locale = models.CharField(max_length=10, default="en")
    timezone = models.CharField(max_length=50, default="UTC")
    currency = models.CharField(max_length=3, default="USD")
    date_format = models.CharField(max_length=20, default="YYYY-MM-DD")
    time_format = models.CharField(max_length=20, default="HH:mm")

    primary_color = models.CharField(
        max_length=7, default="#2563eb", validators=[validate_hex_color]
    )
    secondary_color = models.CharField(
        max_length=7, default="#64748b", validators=[validate_hex_color]
    )
    accent_color = models.CharField(
        max_length=7, default="#0ea5e9", validators=[validate_hex_color]
    )
    font_family = models.CharField(max_length=100, default="Inter")
    favicon = models.ImageField(
        upload_to="company_favicons/", blank=True, null=True
    )
    custom_css = models.TextField(blank=True)
    branding_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "company_settings"
        verbose_name = "Company Setting"
        verbose_name_plural = "Company Settings"

    def __str__(self):
        return f"Settings for {self.company.company_name}"


class CompanyOnboarding(models.Model):
    """
    Tracks the tenant onboarding workflow state for a company.
    """

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name="onboarding",
    )

    profile_completed = models.BooleanField(default=False)
    branding_completed = models.BooleanField(default=False)
    members_added = models.BooleanField(default=False)
    subscription_active = models.BooleanField(default=False)
    first_project_created = models.BooleanField(default=False)

    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    STEPS = (
        "profile_completed",
        "branding_completed",
        "members_added",
        "subscription_active",
        "first_project_created",
    )

    class Meta:
        db_table = "company_onboarding"
        verbose_name = "Company Onboarding"
        verbose_name_plural = "Company Onboarding"

    def __str__(self):
        return f"Onboarding for {self.company.company_name}"

    @property
    def is_completed(self) -> bool:
        return all(getattr(self, step) for step in self.STEPS)

    @property
    def progress(self) -> int:
        completed = sum(1 for step in self.STEPS if getattr(self, step))
        return round(completed / len(self.STEPS) * 100)

    def complete_step(self, step: str, value: bool = True) -> None:
        if step not in self.STEPS:
            raise ValueError(f"Unknown onboarding step: {step}")
        setattr(self, step, value)
        self.completed_at = timezone.now() if self.is_completed else None
        self.save(update_fields=[step, "completed_at", "updated_at"])

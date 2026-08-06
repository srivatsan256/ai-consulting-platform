from django.contrib import admin
from .models import Company, CompanySettings, CompanyOnboarding


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "industry",
        "status",
        "is_active",
        "email",
        "phone",
    )

    search_fields = (
        "company_name",
        "industry",
    )

    list_filter = (
        "industry",
        "status",
        "is_active",
    )


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "locale",
        "timezone",
        "currency",
        "branding_enabled",
    )

    search_fields = ("company__company_name",)


@admin.register(CompanyOnboarding)
class CompanyOnboardingAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "profile_completed",
        "branding_completed",
        "members_added",
        "subscription_active",
        "first_project_created",
        "progress",
        "completed_at",
    )

    search_fields = ("company__company_name",)

    list_filter = (
        "profile_completed",
        "branding_completed",
        "members_added",
        "subscription_active",
        "first_project_created",
    )

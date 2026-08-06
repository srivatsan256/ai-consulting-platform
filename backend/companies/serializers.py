from rest_framework import serializers
from .models import Company, CompanySettings, CompanyOnboarding


class CompanySettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanySettings
        fields = [
            "company",
            "locale",
            "timezone",
            "currency",
            "date_format",
            "time_format",
            "primary_color",
            "secondary_color",
            "accent_color",
            "font_family",
            "favicon",
            "custom_css",
            "branding_enabled",
        ]
        read_only_fields = ["company"]


class CompanyOnboardingSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanyOnboarding
        fields = [
            "company",
            "profile_completed",
            "branding_completed",
            "members_added",
            "subscription_active",
            "first_project_created",
            "progress",
            "is_completed",
            "completed_at",
        ]
        read_only_fields = [
            "company",
            "progress",
            "is_completed",
            "completed_at",
        ]


class CompanySerializer(serializers.ModelSerializer):

    settings = CompanySettingsSerializer(read_only=True)
    onboarding_progress = serializers.IntegerField(read_only=True)
    onboarding_completed = serializers.BooleanField(read_only=True)

    class Meta:
        model = Company
        fields = "__all__"

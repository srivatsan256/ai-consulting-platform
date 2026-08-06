from rest_framework import serializers
from .models import (
    SubscriptionPlan,
    CompanySubscription,
    SubscriptionTier,
    SubscriptionStatus,
    FeatureFlag,
    CompanyFeatureOverride,
    UsageRecord,
)


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)

    class Meta:
        model = SubscriptionPlan
        fields = [
            'id',
            'name',
            'code',
            'description',
            'tier',
            'tier_display',
            'price_monthly',
            'price_yearly',
            'max_projects',
            'max_users',
            'max_storage_gb',
            'max_ai_requests_per_month',
            'allows_custom_rag',
            'allows_advanced_reports',
            'allows_custom_integrations',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CompanySubscriptionSerializer(serializers.ModelSerializer):
    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = CompanySubscription
        fields = [
            'id',
            'company',
            'plan',
            'plan_details',
            'status',
            'status_display',
            'trial_start_date',
            'trial_end_date',
            'current_period_start',
            'current_period_end',
            'cancel_at_period_end',
            'is_valid',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'is_valid', 'created_at', 'updated_at']


class UpgradePlanSerializer(serializers.Serializer):
    new_plan_id = serializers.UUIDField(required=True)
    billing_cycle = serializers.ChoiceField(choices=['monthly', 'yearly'], default='monthly')


class FeatureFlagSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeatureFlag
        fields = [
            'id',
            'code',
            'name',
            'description',
            'is_plan_gated',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CompanyFeatureOverrideSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanyFeatureOverride
        fields = [
            'id',
            'company',
            'feature',
            'is_enabled',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UsageRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = UsageRecord
        fields = [
            'id',
            'company',
            'feature',
            'quantity',
            'period_start',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

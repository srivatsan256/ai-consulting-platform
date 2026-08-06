from django.contrib import admin
from .models import (
    SubscriptionPlan,
    CompanySubscription,
    FeatureFlag,
    CompanyFeatureOverride,
    UsageRecord,
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'tier', 'price_monthly', 'price_yearly', 'max_projects', 'max_users', 'is_active']
    list_filter = ['tier', 'is_active']
    search_fields = ['name', 'code', 'description']
    prepopulated_fields = {'code': ('name',)}


@admin.register(CompanySubscription)
class CompanySubscriptionAdmin(admin.ModelAdmin):
    list_display = ['company', 'plan', 'status', 'current_period_start', 'current_period_end', 'cancel_at_period_end']
    list_filter = ['status', 'cancel_at_period_end', 'plan']
    search_fields = ['company__name', 'plan__name']
    raw_id_fields = ['company', 'plan']


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_plan_gated', 'is_active']
    list_filter = ['is_plan_gated', 'is_active']
    search_fields = ['code', 'name', 'description']
    prepopulated_fields = {'code': ('name',)}


@admin.register(CompanyFeatureOverride)
class CompanyFeatureOverrideAdmin(admin.ModelAdmin):
    list_display = ['company', 'feature', 'is_enabled']
    list_filter = ['is_enabled', 'feature']
    search_fields = ['company__company_name', 'feature__code']
    raw_id_fields = ['company', 'feature']


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = ['company', 'feature', 'quantity', 'period_start']
    list_filter = ['feature', 'period_start']
    search_fields = ['company__company_name', 'feature']
    raw_id_fields = ['company']

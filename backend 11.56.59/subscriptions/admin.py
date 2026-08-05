from django.contrib import admin
from .models import SubscriptionPlan, CompanySubscription


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

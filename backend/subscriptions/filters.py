import django_filters
from .models import SubscriptionPlan, CompanySubscription


class SubscriptionPlanFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    tier = django_filters.CharFilter(field_name='tier')
    is_active = django_filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = SubscriptionPlan
        fields = ['name', 'tier', 'is_active']


class CompanySubscriptionFilter(django_filters.FilterSet):
    company_id = django_filters.UUIDFilter(field_name='company__id')
    status = django_filters.CharFilter(field_name='status')
    plan_tier = django_filters.CharFilter(field_name='plan__tier')

    class Meta:
        model = CompanySubscription
        fields = ['company_id', 'status', 'plan_tier']

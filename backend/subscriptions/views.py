from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import (
    SubscriptionPlan,
    CompanySubscription,
    FeatureFlag,
    CompanyFeatureOverride,
)
from .serializers import (
    SubscriptionPlanSerializer,
    CompanySubscriptionSerializer,
    UpgradePlanSerializer,
    FeatureFlagSerializer,
    CompanyFeatureOverrideSerializer,
)
from .filters import SubscriptionPlanFilter, CompanySubscriptionFilter
from .permissions import IsPlatformAdminOrReadOnly, IsTenantMemberOrAdmin
from .services.service import SubscriptionService
from .services.feature_flag_service import FeatureFlagService
from .services.usage_service import QuotaService, UsageService


@extend_schema_view(
    list=extend_schema(summary="List all available subscription plans"),
    create=extend_schema(summary="Create a new subscription plan (Admin only)"),
    retrieve=extend_schema(summary="Retrieve plan details"),
    update=extend_schema(summary="Update a subscription plan (Admin only)"),
    destroy=extend_schema(summary="Delete a subscription plan (Admin only)")
)
class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsPlatformAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SubscriptionPlanFilter
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['price_monthly', 'created_at']
    ordering = ['price_monthly']


@extend_schema_view(
    list=extend_schema(summary="List company subscriptions"),
    retrieve=extend_schema(summary="Retrieve subscription details"),
)
class CompanySubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CompanySubscription.objects.select_related('company', 'plan').all()
    serializer_class = CompanySubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantMemberOrAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CompanySubscriptionFilter
    ordering_fields = ['created_at', 'current_period_end']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_superuser', False):
            return self.queryset
        tenant = getattr(self.request, 'tenant', None)
        if tenant and tenant.company:
            return self.queryset.filter(company=tenant.company)
        return self.queryset.none()

    @extend_schema(request=UpgradePlanSerializer, responses={200: CompanySubscriptionSerializer})
    @action(detail=True, methods=['post'], url_path='upgrade')
    def upgrade(self, request, pk=None):
        """Upgrade or change current subscription plan."""
        subscription = self.get_object()
        serializer = UpgradePlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            new_plan = SubscriptionPlan.objects.get(
                id=serializer.validated_data['new_plan_id'],
                is_active=True
            )
        except SubscriptionPlan.DoesNotExist:
            return Response({'detail': 'Plan not found or inactive.'}, status=status.HTTP_404_NOT_FOUND)

        updated_sub = SubscriptionService.upgrade_or_downgrade(
            subscription=subscription,
            new_plan=new_plan,
            billing_cycle=serializer.validated_data.get('billing_cycle', 'monthly')
        )
        return Response(CompanySubscriptionSerializer(updated_sub).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """Cancel subscription."""
        subscription = self.get_object()
        immediate = request.data.get('immediate', False)
        canceled_sub = SubscriptionService.cancel_subscription(subscription, immediate=immediate)
        return Response(CompanySubscriptionSerializer(canceled_sub).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Feature flags for the tenant")
    @action(detail=False, methods=['get'], url_path='features')
    def features(self, request):
        """List resolved feature flags for the requesting tenant."""
        tenant = getattr(request, 'tenant', None)
        if not tenant or not tenant.company:
            return Response({'detail': 'No company associated with this user.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(FeatureFlagService.get_feature_map(tenant.company))

    @extend_schema(summary="Monthly usage for the tenant")
    @action(detail=False, methods=['get'], url_path='usage')
    def usage(self, request):
        """Usage report for the requesting tenant's current month."""
        tenant = getattr(request, 'tenant', None)
        if not tenant or not tenant.company:
            return Response({'detail': 'No company associated with this user.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'period': UsageService.get_monthly_report(tenant.company)})

    @extend_schema(summary="Quota overview for the tenant")
    @action(detail=False, methods=['get'], url_path='quotas')
    def quotas(self, request):
        """Plan limits and usage for the requesting tenant."""
        tenant = getattr(request, 'tenant', None)
        if not tenant or not tenant.company:
            return Response({'detail': 'No company associated with this user.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(QuotaService.get_report(tenant.company))


@extend_schema_view(
    list=extend_schema(summary="List feature flags"),
    create=extend_schema(summary="Create a feature flag (Admin only)"),
    retrieve=extend_schema(summary="Retrieve a feature flag"),
    update=extend_schema(summary="Update a feature flag (Admin only)"),
    destroy=extend_schema(summary="Delete a feature flag (Admin only)"),
)
class FeatureFlagViewSet(viewsets.ModelViewSet):
    queryset = FeatureFlag.objects.all()
    serializer_class = FeatureFlagSerializer
    permission_classes = [IsPlatformAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'created_at']
    ordering = ['code']


class CompanyFeatureOverrideViewSet(viewsets.ModelViewSet):
    """
    Platform admin management of per-company feature flag overrides.
    """
    queryset = CompanyFeatureOverride.objects.select_related('company', 'feature')
    serializer_class = CompanyFeatureOverrideSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company', 'feature', 'is_enabled']

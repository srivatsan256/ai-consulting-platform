from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubscriptionPlanViewSet,
    CompanySubscriptionViewSet,
    FeatureFlagViewSet,
    CompanyFeatureOverrideViewSet,
)

router = DefaultRouter()
router.register(r'plans', SubscriptionPlanViewSet, basename='subscription-plan')
router.register(r'subscriptions', CompanySubscriptionViewSet, basename='company-subscription')
router.register(r'feature-flags', FeatureFlagViewSet, basename='feature-flag')
router.register(r'feature-overrides', CompanyFeatureOverrideViewSet, basename='company-feature-override')

urlpatterns = [
    path('', include(router.urls)),
]

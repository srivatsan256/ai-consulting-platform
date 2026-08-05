from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import SystemSettingViewSet, UserProfileViewSet

router = DefaultRouter()

router.register(
    "system",
    SystemSettingViewSet,
    basename="systemsetting",
)

router.register(
    "profile",
    UserProfileViewSet,
    basename="userprofile",
)

urlpatterns = [
    path("", include(router.urls)),
]

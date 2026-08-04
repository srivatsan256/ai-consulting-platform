from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import NotificationViewSet, NotificationPreferenceViewSet

router = DefaultRouter()

router.register(
    "",
    NotificationViewSet,
    basename="notification",
)

router.register(
    "preferences",
    NotificationPreferenceViewSet,
    basename="notificationpreference",
)

urlpatterns = [
    path("", include(router.urls)),
]

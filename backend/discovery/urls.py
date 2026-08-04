from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import DiscoveryViewSet

router = DefaultRouter()

router.register(
    "",
    DiscoveryViewSet,
    basename="discovery"
)

urlpatterns = [
    path("", include(router.urls)),
]
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import MonitoringAlertViewSet, SystemMetricViewSet

router = DefaultRouter()

router.register(
    "alerts",
    MonitoringAlertViewSet,
    basename="monitoringalert",
)

router.register(
    "metrics",
    SystemMetricViewSet,
    basename="systemmetric",
)

urlpatterns = [
    path("", include(router.urls)),
]

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import DashboardWidgetViewSet

router = DefaultRouter()

router.register(
    "widgets",
    DashboardWidgetViewSet,
    basename="dashboardwidget",
)

urlpatterns = [
    path("", include(router.urls)),
]

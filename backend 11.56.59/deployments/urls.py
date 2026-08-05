from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import DeploymentViewSet

router = DefaultRouter()

router.register(
    "",
    DeploymentViewSet,
    basename="deployment",
)

urlpatterns = [
    path("", include(router.urls)),
]

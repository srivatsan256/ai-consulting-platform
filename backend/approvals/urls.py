from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import ApprovalViewSet

router = DefaultRouter()

router.register(
    "",
    ApprovalViewSet,
    basename="approval",
)

urlpatterns = [
    path("", include(router.urls)),
]

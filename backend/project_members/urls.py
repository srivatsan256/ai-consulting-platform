from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProjectMemberViewSet

router = DefaultRouter()
router.register("", ProjectMemberViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
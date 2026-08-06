from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TeamViewSet, TeamMemberViewSet

router = DefaultRouter()

router.register("", TeamViewSet, basename="team")

router.register(
    "members",
    TeamMemberViewSet,
    basename="teammember",
)

urlpatterns = [
    path("", include(router.urls)),
]

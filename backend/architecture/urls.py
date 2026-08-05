from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import ArchitectureDiagramViewSet, TechnologyStackViewSet

router = DefaultRouter()

router.register(
    "diagrams",
    ArchitectureDiagramViewSet,
    basename="architecturediagram",
)

router.register(
    "tech-stack",
    TechnologyStackViewSet,
    basename="technologystack",
)

urlpatterns = [
    path("", include(router.urls)),
]

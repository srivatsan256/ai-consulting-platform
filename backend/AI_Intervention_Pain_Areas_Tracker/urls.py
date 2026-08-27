from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AIInterventionPainAreaViewSet,
    RoadmapViewSet,
    AssistantView,
    DepartmentStatsViewSet,
)

router = DefaultRouter()
router.register("", AIInterventionPainAreaViewSet, basename="pain-area")

urlpatterns = [
    path("roadmap/", RoadmapViewSet.as_view({"get": "list"}), name="roadmap"),
    path("ai-assistant/", AssistantView.as_view({"post": "create"}), name="ai-assistant"),
    path(
        "department-stats/",
        DepartmentStatsViewSet.as_view({"get": "list"}),
        name="department-stats-list",
    ),
    path(
        "department-stats/<str:pk>/",
        DepartmentStatsViewSet.as_view({"get": "retrieve"}),
        name="department-stats-detail",
    ),
    path("", include(router.urls)),
]

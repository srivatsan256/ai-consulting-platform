from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AIInterventionPainAreaViewSet, RoadmapViewSet, AssistantView

router = DefaultRouter()
router.register("", AIInterventionPainAreaViewSet, basename="pain-area")

urlpatterns = [
    path("", include(router.urls)),
    path("roadmap/", RoadmapViewSet.as_view({"get": "list"}), name="roadmap"),
    path("ai-assistant/", AssistantView.as_view({"post": "create"}), name="ai-assistant"),
]

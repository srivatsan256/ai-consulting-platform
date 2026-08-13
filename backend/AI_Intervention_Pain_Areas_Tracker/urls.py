from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AIInterventionPainAreaViewSet

router = DefaultRouter()
router.register("", AIInterventionPainAreaViewSet, basename="pain-area")

urlpatterns = [
    path("", include(router.urls)),
]

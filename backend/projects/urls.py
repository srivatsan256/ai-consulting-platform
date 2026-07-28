from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, DocumentUploadView
from verification.views import VerifyAllView, ValidateDiscoveryView, LevelModuleViewSet

router = DefaultRouter()
router.register(r"", ProjectViewSet, basename="project")

level_module_router = DefaultRouter()
level_module_router.register(r"", LevelModuleViewSet, basename="level-module")

urlpatterns = [
    path("level-modules/", include(level_module_router.urls)),
    path("", include(router.urls)),
    path("<uuid:pk>/documents/", DocumentUploadView.as_view(), name="document-upload"),
    path("<uuid:pk>/verify_all/", VerifyAllView.as_view(), name="verify-all"),
    path("<uuid:pk>/validate_discovery/", ValidateDiscoveryView.as_view(), name="validate-discovery"),
]

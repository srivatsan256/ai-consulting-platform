from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet,
    ProjectPhaseViewSet,
    MilestoneViewSet,
    LevelModuleListView,
    ProjectListCreateView,
    ProjectDetailView,
    ProjectDocumentUploadView,
    ProjectVerifyView,
    ProjectChatView,
    ProjectDeliverablesView,
    RequiredDocStatusView,
)

router = DefaultRouter()

router.register("projects", ProjectViewSet)
router.register("phases", ProjectPhaseViewSet)
router.register("milestones", MilestoneViewSet)

urlpatterns = [
    path("level-modules/", LevelModuleListView.as_view(), name="level-modules"),
    path("", ProjectListCreateView.as_view()),
    path("<int:pk>/", ProjectDetailView.as_view()),
    path("<int:pk>/documents/", ProjectDocumentUploadView.as_view()),
    path("<int:pk>/verify_all/", ProjectVerifyView.as_view()),
    path("<int:pk>/chat/", ProjectChatView.as_view()),
    path("<int:pk>/generate_deliverables/", ProjectDeliverablesView.as_view()),
    path("<int:pk>/required_doc_status/", RequiredDocStatusView.as_view()),
    path("", include(router.urls)),
]

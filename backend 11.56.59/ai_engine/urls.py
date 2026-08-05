from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import AIAssessmentViewSet, AIUseCaseViewSet
from .prompt_views import prompt_list, prompt_detail, prompt_preview

router = DefaultRouter()

router.register(
    "assessments",
    AIAssessmentViewSet,
    basename="aiassessment",
)

router.register(
    "use-cases",
    AIUseCaseViewSet,
    basename="aiusecase",
)

urlpatterns = [
    path("", include(router.urls)),
    path("prompts/", prompt_list, name="prompt-list"),
    path("prompts/<str:template_name>/", prompt_detail, name="prompt-detail"),
    path("prompts/<str:template_name>/preview/", prompt_preview, name="prompt-preview"),
]

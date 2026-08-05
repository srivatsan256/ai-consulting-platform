from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import KnowledgeBaseViewSet

router = DefaultRouter()

router.register(
    "",
    KnowledgeBaseViewSet,
    basename="knowledgebase",
)

urlpatterns = [
    path("", include(router.urls)),
]

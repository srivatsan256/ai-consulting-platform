from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import SecurityChecklistViewSet, VulnerabilityReportViewSet

router = DefaultRouter()

router.register(
    "checklists",
    SecurityChecklistViewSet,
    basename="securitychecklist",
)

router.register(
    "vulnerabilities",
    VulnerabilityReportViewSet,
    basename="vulnerabilityreport",
)

urlpatterns = [
    path("", include(router.urls)),
]

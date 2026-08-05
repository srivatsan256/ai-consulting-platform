from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyMemberViewSet

router = DefaultRouter()
router.register("memberships", CompanyMemberViewSet, basename="companymember")

urlpatterns = [
    path("", include(router.urls)),
]

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import DepartmentMemberViewSet, DepartmentViewSet

router = DefaultRouter()

router.register(
    "",
    DepartmentViewSet,
    basename="department",
)

members_router = DefaultRouter()

members_router.register(
    "",
    DepartmentMemberViewSet,
    basename="department-member",
)

urlpatterns = [
    path("members/", include(members_router.urls)),
    path("", include(router.urls)),
]

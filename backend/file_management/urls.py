from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    FileCategoryViewSet,
    FileManagementViewSet,
    FilePermissionViewSet,
    FileScanViewSet,
    StorageQuotaViewSet,
)

router = DefaultRouter()

router.register(
    "files",
    FileManagementViewSet,
    basename="filemanagement",
)

router.register(
    "categories",
    FileCategoryViewSet,
    basename="filecategory",
)

router.register(
    "quota",
    StorageQuotaViewSet,
    basename="storagequota",
)

router.register(
    "scans",
    FileScanViewSet,
    basename="filescan",
)

router.register(
    "permissions",
    FilePermissionViewSet,
    basename="filepermission",
)

urlpatterns = [
    path("", include(router.urls)),
]

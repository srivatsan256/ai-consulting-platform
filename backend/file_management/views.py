from django.db.models import Count
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.enforcement import TenantEnforcement
from core.tenant_scoping import TenantScopedViewSetMixin
from projects.models import Project, ProjectDocument
from projects.services.verification_service import extract_text, verify_document

from .filters import (
    FileCategoryFilter,
    FileManagementFilter,
    FilePermissionFilter,
    FileScanFilter,
)
from .models import FileCategory, FilePermission, FileScan, StorageQuota
from .serializers import (
    FileCategorySerializer,
    FileManagementSerializer,
    FilePermissionSerializer,
    FileScanSerializer,
    StorageQuotaSerializer,
)
from .services.access import check_file_access
from .services.scanner import run_virus_scan
from .utils.upload import create_project_document


class FileCategoryViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    """Company-scoped categories used to organise uploaded files."""

    serializer_class = FileCategorySerializer

    queryset = FileCategory.objects.annotate(
        file_count=Count("files"),
    )

    filterset_class = FileCategoryFilter

    search_fields = ["name", "description"]

    ordering_fields = ["name", "created_at", "updated_at"]

    ordering = ["name"]

    permission_classes = [IsAuthenticated]


class StorageQuotaViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    """Storage allowance for the current tenant company."""

    serializer_class = StorageQuotaSerializer

    queryset = StorageQuota.objects.all()

    http_method_names = ["get", "put", "patch"]

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        tenant = getattr(self.request, "tenant", None)
        if tenant and tenant.company:
            StorageQuota.get_for_company(tenant.company)
        return super().get_queryset()

    def list(self, request, *args, **kwargs):
        tenant = TenantEnforcement.require_tenant(request)
        quota = StorageQuota.get_for_company(tenant.company)
        return Response(self.get_serializer(quota).data)

    def retrieve(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        tenant = TenantEnforcement.require_tenant(request)
        quota = StorageQuota.get_for_company(tenant.company)
        serializer = self.get_serializer(quota, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class FileScanViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    """Virus-scan results for uploaded project files."""

    serializer_class = FileScanSerializer

    queryset = FileScan.objects.select_related("file", "file__project")

    filterset_class = FileScanFilter

    ordering_fields = ["updated_at", "status"]

    ordering = ["-updated_at"]

    http_method_names = ["get", "post"]

    permission_classes = [IsAuthenticated]

    tenant_lookup_path = "file__project__company"

    @action(detail=True, methods=["post"])
    def rescan(self, request, pk=None):
        scan = self.get_object()
        updated = run_virus_scan(scan.file)
        return Response(self.get_serializer(updated).data)


class FilePermissionViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    """Granular access rules for uploaded project files."""

    serializer_class = FilePermissionSerializer

    queryset = FilePermission.objects.select_related(
        "file",
        "user",
        "granted_by",
    )

    filterset_class = FilePermissionFilter

    ordering_fields = ["created_at"]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

    tenant_lookup_path = "file__project__company"


class FileManagementViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):
    """Rich view of project files for the File Management module."""

    serializer_class = FileManagementSerializer

    queryset = ProjectDocument.objects.select_related(
        "project",
        "project__company",
        "uploaded_by",
        "file_category",
    ).prefetch_related("scan", "permissions")

    filterset_class = FileManagementFilter

    search_fields = ["original_name", "doc_type"]

    ordering_fields = ["uploaded_at", "file_size", "original_name"]

    ordering = ["-uploaded_at"]

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(project__is_active=True)

    def create(self, request, *args, **kwargs):
        tenant = TenantEnforcement.require_tenant(request)
        file_obj = request.FILES.get("file")
        if file_obj is None:
            return Response(
                {"detail": "A file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project = get_object_or_404(
            Project.objects.filter(
                company=tenant.company,
                is_active=True,
            ),
            pk=request.data.get("project"),
        )

        document = create_project_document(
            project=project,
            file_obj=file_obj,
            original_name=file_obj.name,
            doc_type=request.data.get("doc_type", "OTHER"),
            level=request.data.get("level"),
            category_id=request.data.get("file_category"),
            user=request.user,
        )

        extract_text(document)
        verify_document(document)

        return Response(
            self.get_serializer(document).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def rescan(self, request, pk=None):
        document = self.get_object()
        updated = run_virus_scan(document)
        return Response(FileScanSerializer(updated).data)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        document = self.get_object()
        if not check_file_access(request.user, document, "download"):
            return Response(
                {"detail": "You do not have permission to download this file."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not document.file:
            return Response(
                {"detail": "File is missing."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return FileResponse(
            document.file.open("rb"),
            as_attachment=True,
            filename=document.original_name or document.file.name,
        )

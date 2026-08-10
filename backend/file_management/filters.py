import django_filters

from projects.models import ProjectDocument

from .models import FileCategory, FilePermission, FileScan


class FileCategoryFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = FileCategory
        fields = ["name"]


class FileScanFilter(django_filters.FilterSet):

    status = django_filters.CharFilter(lookup_expr="iexact")

    file = django_filters.NumberFilter()

    class Meta:
        model = FileScan
        fields = ["status", "file", "scanner"]


class FilePermissionFilter(django_filters.FilterSet):

    file = django_filters.NumberFilter()

    user = django_filters.NumberFilter()

    permission = django_filters.CharFilter(lookup_expr="iexact")

    role_key = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = FilePermission
        fields = ["file", "user", "permission", "role_key"]


class FileManagementFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    doc_type = django_filters.CharFilter(lookup_expr="iexact")

    level = django_filters.NumberFilter()

    file_category = django_filters.NumberFilter()

    verification_status = django_filters.BooleanFilter()

    scan_status = django_filters.CharFilter(
        method="filter_scan_status",
        label="Scan status (clean/infected/pending/error)",
    )

    def filter_scan_status(self, queryset, name, value):
        if value:
            return queryset.filter(scan__status__iexact=value)
        return queryset

    class Meta:
        model = ProjectDocument
        fields = [
            "project",
            "doc_type",
            "level",
            "file_category",
            "verification_status",
        ]

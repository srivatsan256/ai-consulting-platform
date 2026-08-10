from rest_framework import serializers

from projects.models import ProjectDocument

from .models import FileCategory, FilePermission, FileScan, StorageQuota


class FileCategorySerializer(serializers.ModelSerializer):
    file_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = FileCategory
        fields = [
            "id",
            "name",
            "color",
            "icon",
            "description",
            "file_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data):
        company = self.context["request"].tenant.company
        return FileCategory.objects.create(company=company, **validated_data)


class StorageQuotaSerializer(serializers.ModelSerializer):
    used_bytes = serializers.IntegerField(read_only=True)
    remaining_bytes = serializers.IntegerField(read_only=True)
    usage_percent = serializers.FloatField(read_only=True)
    quota_limit_display = serializers.SerializerMethodField()
    used_display = serializers.SerializerMethodField()

    class Meta:
        model = StorageQuota
        fields = [
            "id",
            "quota_limit_bytes",
            "quota_limit_display",
            "used_bytes",
            "used_display",
            "remaining_bytes",
            "usage_percent",
            "enforced",
            "updated_at",
        ]
        read_only_fields = ("id", "updated_at")

    def get_quota_limit_display(self, obj):
        from .services.storage import format_bytes

        return format_bytes(obj.quota_limit_bytes)

    def get_used_display(self, obj):
        from .services.storage import format_bytes

        return format_bytes(obj.used_bytes)


class FileScanSerializer(serializers.ModelSerializer):
    file_name = serializers.CharField(source="file.original_name", read_only=True)

    class Meta:
        model = FileScan
        fields = [
            "id",
            "file",
            "file_name",
            "status",
            "scanner",
            "signature",
            "findings",
            "scanned_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class FilePermissionSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source="user.email", read_only=True, allow_null=True)
    role_key = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = FilePermission
        fields = [
            "id",
            "file",
            "user",
            "user_name",
            "user_email",
            "role_key",
            "permission",
            "allow",
            "granted_by",
            "created_at",
        ]
        read_only_fields = ("id", "granted_by", "created_at")

    def get_user_name(self, obj):
        if obj.user_id:
            return obj.user.get_full_name() or obj.user.email
        return ""

    def create(self, validated_data):
        validated_data["granted_by"] = self.context["request"].user
        return super().create(validated_data)


class FileManagementSerializer(serializers.ModelSerializer):
    """Rich view of a project file for the File Management module."""

    file_url = serializers.SerializerMethodField()
    category = FileCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=FileCategory.objects.none(),
        source="file_category",
        write_only=True,
        required=False,
    )
    scan = FileScanSerializer(read_only=True)
    permissions = FilePermissionSerializer(many=True, read_only=True)
    permission_count = serializers.IntegerField(read_only=True)
    project_name = serializers.CharField(source="project.project_name", read_only=True)
    company_name = serializers.CharField(source="project.company.company_name", read_only=True)
    size_display = serializers.SerializerMethodField()
    uploaded_by_name = serializers.SerializerMethodField()
    can_download = serializers.SerializerMethodField()

    class Meta:
        model = ProjectDocument
        fields = [
            "id",
            "project",
            "project_name",
            "company_name",
            "file",
            "file_url",
            "file_size",
            "size_display",
            "original_name",
            "doc_type",
            "file_category",
            "category",
            "category_id",
            "level",
            "extracted_text",
            "verification_status",
            "verification_score",
            "missing_requirements",
            "scan",
            "permissions",
            "permission_count",
            "uploaded_at",
            "uploaded_by",
            "uploaded_by_name",
            "can_download",
        ]
        read_only_fields = [
            "id",
            "file",
            "file_url",
            "file_size",
            "size_display",
            "original_name",
            "extracted_text",
            "verification_status",
            "verification_score",
            "missing_requirements",
            "scan",
            "permissions",
            "permission_count",
            "uploaded_at",
            "uploaded_by",
            "uploaded_by_name",
            "can_download",
        ]

    def get_file_url(self, obj):
        return obj.file.url if obj.file else None

    def get_size_display(self, obj):
        from .services.storage import format_bytes

        return format_bytes(obj.file_size)

    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by_id:
            return obj.uploaded_by.get_full_name() or obj.uploaded_by.email
        return ""

    def get_can_download(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        from .services.access import check_file_access

        return check_file_access(request.user, obj, "download")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None:
            tenant = getattr(request, "tenant", None)
            if tenant is not None:
                self.fields["category_id"].queryset = FileCategory.objects.filter(
                    company=tenant.company
                )

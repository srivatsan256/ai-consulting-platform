from django.contrib import admin

from .models import FileCategory, FilePermission, FileScan, StorageQuota


@admin.register(FileCategory)
class FileCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "company",
        "color",
        "icon",
        "description",
    )

    list_filter = ("company",)

    search_fields = ("name", "description")


@admin.register(StorageQuota)
class StorageQuotaAdmin(admin.ModelAdmin):

    list_display = (
        "company",
        "quota_limit_bytes",
        "enforced",
        "updated_at",
    )

    list_filter = ("enforced",)


@admin.register(FileScan)
class FileScanAdmin(admin.ModelAdmin):

    list_display = (
        "file",
        "status",
        "scanner",
        "signature",
        "scanned_at",
    )

    list_filter = ("status", "scanner")

    search_fields = ("file__original_name", "signature")


@admin.register(FilePermission)
class FilePermissionAdmin(admin.ModelAdmin):

    list_display = (
        "file",
        "user",
        "role_key",
        "permission",
        "allow",
        "granted_by",
        "created_at",
    )

    list_filter = ("permission", "allow")

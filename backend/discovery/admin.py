from django.contrib import admin

from .models import (
    Discovery,
    DiscoveryText,
    DiscoveryDocument,
)


@admin.register(Discovery)
class DiscoveryAdmin(admin.ModelAdmin):

    list_display = (
        "project",
        "input_type",
        "status",
        "version",
        "created_by",
        "created_at",
    )

    list_filter = (
        "input_type",
        "status",
    )

    search_fields = (
        "project__project_name",
    )


@admin.register(DiscoveryText)
class DiscoveryTextAdmin(admin.ModelAdmin):

    list_display = (
        "discovery",
        "business_problem",
    )


@admin.register(DiscoveryDocument)
class DiscoveryDocumentAdmin(admin.ModelAdmin):

    list_display = (
        "discovery",
        "original_filename",
        "total_pages",
        "upload_time",
    )

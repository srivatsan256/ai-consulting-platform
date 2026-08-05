from django.contrib import admin
from .models import Permission


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):

    list_display = (
        "role",
        "feature",
        "can_view",
        "can_create",
        "can_update",
        "can_delete",
        "can_review",
        "can_approve",
        "can_export",
    )

    list_filter = (
        "role",
        "feature",
    )

    search_fields = (
        "role__display_name",
        "feature",
    )
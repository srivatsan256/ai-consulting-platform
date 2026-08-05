from django.contrib import admin

from .models import Approval


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "entity_type",
        "project",
        "status",
        "requested_by",
        "assigned_to",
        "created_at",
    )

    list_filter = (
        "status",
        "entity_type",
    )

    search_fields = (
        "title",
        "description",
    )

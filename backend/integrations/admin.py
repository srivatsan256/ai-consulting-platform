from django.contrib import admin

from .models import Integration


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "project",
        "integration_type",
        "status",
        "last_sync_at",
        "created_at",
    )

    list_filter = (
        "status",
        "integration_type",
    )

    search_fields = (
        "name",
    )

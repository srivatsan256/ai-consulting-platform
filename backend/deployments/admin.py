from django.contrib import admin

from .models import Deployment


@admin.register(Deployment)
class DeploymentAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "project",
        "version",
        "environment",
        "status",
        "deployed_by",
        "deployed_at",
    )

    list_filter = (
        "status",
        "environment",
    )

    search_fields = (
        "title",
        "description",
        "version",
    )

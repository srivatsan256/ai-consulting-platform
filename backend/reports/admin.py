from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "project",
        "report_type",
        "status",
        "created_by",
        "created_at",
    )

    list_filter = (
        "status",
        "report_type",
    )

    search_fields = (
        "title",
        "content",
    )

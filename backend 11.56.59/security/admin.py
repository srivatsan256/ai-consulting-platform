from django.contrib import admin

from .models import SecurityChecklist, VulnerabilityReport


@admin.register(SecurityChecklist)
class SecurityChecklistAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "project",
        "category",
        "status",
        "assigned_to",
        "due_date",
    )

    list_filter = (
        "status",
        "category",
    )

    search_fields = (
        "title",
        "description",
    )


@admin.register(VulnerabilityReport)
class VulnerabilityReportAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "project",
        "severity",
        "status",
        "affected_component",
        "reported_date",
    )

    list_filter = (
        "severity",
        "status",
    )

    search_fields = (
        "title",
        "description",
    )

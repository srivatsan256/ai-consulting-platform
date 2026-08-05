from django.contrib import admin

from .models import Risk


@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "project",
        "severity",
        "probability",
        "status",
        "owner",
        "identified_date",
    )

    list_filter = (
        "status",
        "severity",
        "probability",
    )

    search_fields = (
        "title",
        "description",
    )

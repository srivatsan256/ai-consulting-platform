from django.contrib import admin

from .models import DashboardWidget


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "widget_type",
        "owner",
        "project",
        "position",
        "is_visible",
    )

    list_filter = (
        "widget_type",
        "is_visible",
    )

    search_fields = (
        "title",
    )

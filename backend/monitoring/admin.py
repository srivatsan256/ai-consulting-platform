from django.contrib import admin

from .models import MonitoringAlert, SystemMetric


@admin.register(MonitoringAlert)
class MonitoringAlertAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "project",
        "severity",
        "status",
        "source",
        "created_at",
    )

    list_filter = (
        "severity",
        "status",
    )

    search_fields = (
        "title",
        "message",
    )


@admin.register(SystemMetric)
class SystemMetricAdmin(admin.ModelAdmin):

    list_display = (
        "metric_name",
        "project",
        "metric_value",
        "unit",
        "recorded_at",
    )

    search_fields = (
        "metric_name",
    )

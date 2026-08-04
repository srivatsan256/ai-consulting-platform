from rest_framework import serializers

from .models import MonitoringAlert, SystemMetric


class MonitoringAlertSerializer(serializers.ModelSerializer):

    acknowledged_by_name = serializers.CharField(
        source="acknowledged_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = MonitoringAlert
        fields = [
            "id",
            "project",
            "title",
            "message",
            "severity",
            "status",
            "source",
            "metric_name",
            "metric_value",
            "threshold",
            "acknowledged_by",
            "acknowledged_by_name",
            "resolved_at",
            "created_at",
        ]
        read_only_fields = (
            "id",
            "acknowledged_by",
            "resolved_at",
            "created_at",
        )


class SystemMetricSerializer(serializers.ModelSerializer):

    class Meta:
        model = SystemMetric
        fields = [
            "id",
            "project",
            "metric_name",
            "metric_value",
            "unit",
            "source",
            "recorded_at",
        ]
        read_only_fields = (
            "id",
            "recorded_at",
        )

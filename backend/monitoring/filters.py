import django_filters

from .models import MonitoringAlert, SystemMetric


class MonitoringAlertFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    severity = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    status = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    class Meta:
        model = MonitoringAlert
        fields = [
            "project",
            "severity",
            "status",
        ]


class SystemMetricFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    metric_name = django_filters.CharFilter(
        lookup_expr="icontains",
    )

    class Meta:
        model = SystemMetric
        fields = [
            "project",
            "metric_name",
        ]

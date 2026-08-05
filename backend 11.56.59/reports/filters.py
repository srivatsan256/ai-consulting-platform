import django_filters

from .models import Report


class ReportFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    report_type = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    status = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    class Meta:
        model = Report
        fields = [
            "project",
            "report_type",
            "status",
        ]

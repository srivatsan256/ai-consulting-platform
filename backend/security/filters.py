import django_filters

from .models import SecurityChecklist, VulnerabilityReport


class SecurityChecklistFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    category = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    status = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    assigned_to = django_filters.NumberFilter()

    class Meta:
        model = SecurityChecklist
        fields = [
            "project",
            "category",
            "status",
            "assigned_to",
        ]


class VulnerabilityReportFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    severity = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    status = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    class Meta:
        model = VulnerabilityReport
        fields = [
            "project",
            "severity",
            "status",
        ]

import django_filters

from .models import Risk


class RiskFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    status = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    severity = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    probability = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    owner = django_filters.NumberFilter()

    class Meta:
        model = Risk
        fields = [
            "project",
            "status",
            "severity",
            "probability",
            "owner",
        ]

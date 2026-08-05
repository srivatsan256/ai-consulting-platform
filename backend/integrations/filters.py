import django_filters

from .models import Integration


class IntegrationFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    integration_type = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    status = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    class Meta:
        model = Integration
        fields = [
            "project",
            "integration_type",
            "status",
        ]

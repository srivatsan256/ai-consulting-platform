import django_filters
from .models import Discovery


class DiscoveryFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    status = django_filters.CharFilter(lookup_expr="iexact")

    input_type = django_filters.CharFilter(lookup_expr="iexact")

    ai_processed = django_filters.BooleanFilter()

    class Meta:
        model = Discovery
        fields = [
            "project",
            "status",
            "input_type",
            "ai_processed",
        ]

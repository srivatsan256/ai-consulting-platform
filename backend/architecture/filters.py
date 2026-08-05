import django_filters

from .models import ArchitectureDiagram, TechnologyStack


class ArchitectureDiagramFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    category = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    class Meta:
        model = ArchitectureDiagram
        fields = [
            "project",
            "category",
        ]


class TechnologyStackFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    category = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    is_active = django_filters.BooleanFilter()

    class Meta:
        model = TechnologyStack
        fields = [
            "project",
            "category",
            "is_active",
        ]

import django_filters

from core.constants import StatusChoices


class BaseFilter(django_filters.FilterSet):
    """
    Base filter with common filters for all tenant-aware models.
    """

    created_at = django_filters.DateTimeFilter(lookup_expr="gte")
    created_at_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    updated_at = django_filters.DateTimeFilter(lookup_expr="gte")
    updated_at_after = django_filters.DateTimeFilter(field_name="updated_at", lookup_expr="lte")
    created_by = django_filters.NumberFilter(field_name="created_by__id")
    status = django_filters.ChoiceFilter(choices=StatusChoices.choices)
    search = django_filters.CharFilter(method="filter_search")

    def filter_search(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(name__icontains=value)

    class Meta:
        abstract = True
        fields = [
            "created_at",
            "created_at_after",
            "updated_at",
            "updated_at_after",
            "created_by",
            "status",
            "search",
        ]

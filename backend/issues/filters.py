import django_filters

from .models import Issue


class IssueFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    status = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    priority = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    category = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    assigned_to = django_filters.NumberFilter()

    reported_by = django_filters.NumberFilter()

    class Meta:
        model = Issue
        fields = [
            "project",
            "status",
            "priority",
            "category",
            "assigned_to",
            "reported_by",
        ]

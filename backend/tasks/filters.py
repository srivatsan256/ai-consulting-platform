import django_filters

from .models import Task


class TaskFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    status = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    priority = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    assigned_to = django_filters.NumberFilter()

    parent = django_filters.NumberFilter()

    due_before = django_filters.DateFilter(
        field_name="due_date",
        lookup_expr="lte",
    )

    due_after = django_filters.DateFilter(
        field_name="due_date",
        lookup_expr="gte",
    )

    class Meta:
        model = Task
        fields = [
            "project",
            "status",
            "priority",
            "assigned_to",
            "parent",
            "due_before",
            "due_after",
        ]

import django_filters

from .models import DashboardWidget


class DashboardWidgetFilter(django_filters.FilterSet):

    owner = django_filters.NumberFilter()

    widget_type = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    project = django_filters.NumberFilter()

    is_visible = django_filters.BooleanFilter()

    class Meta:
        model = DashboardWidget
        fields = [
            "owner",
            "widget_type",
            "project",
            "is_visible",
        ]

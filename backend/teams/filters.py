import django_filters

from .models import Team


class TeamFilter(django_filters.FilterSet):

    department = django_filters.NumberFilter()

    is_active = django_filters.BooleanFilter()

    team_name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Team
        fields = [
            "department",
            "is_active",
            "team_name",
        ]

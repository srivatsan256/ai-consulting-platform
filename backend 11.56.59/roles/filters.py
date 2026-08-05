import django_filters
from .models import Role


class RoleFilter(django_filters.FilterSet):

    role_key = django_filters.CharFilter(lookup_expr="iexact")

    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Role
        fields = [
            "role_key",
            "is_active",
        ]

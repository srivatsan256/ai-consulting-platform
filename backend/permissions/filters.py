import django_filters
from .models import Permission


class PermissionFilter(django_filters.FilterSet):

    role = django_filters.NumberFilter()

    feature = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Permission
        fields = [
            "role",
            "feature",
        ]

import django_filters
from .models import User


class UserFilter(django_filters.FilterSet):

    email = django_filters.CharFilter(lookup_expr="icontains")

    username = django_filters.CharFilter(lookup_expr="icontains")

    is_active = django_filters.BooleanFilter()

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "is_active",
        ]

import django_filters # type: ignore

from .models import Department


class DepartmentFilter(django_filters.FilterSet):

    company = django_filters.NumberFilter()

    head = django_filters.NumberFilter()

    status = django_filters.CharFilter(
        lookup_expr="iexact"
    )

    name = django_filters.CharFilter(
        lookup_expr="icontains"
    )

    code = django_filters.CharFilter(
        lookup_expr="icontains"
    )

    class Meta:
        model = Department

        fields = [
            "company",
            "head",
            "status",
            "name",
            "code",
        ]
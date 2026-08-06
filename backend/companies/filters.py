import django_filters
from .models import Company


class CompanyFilter(django_filters.FilterSet):

    company_name = django_filters.CharFilter(lookup_expr="icontains")

    industry = django_filters.CharFilter(lookup_expr="icontains")

    is_active = django_filters.BooleanFilter()

    status = django_filters.CharFilter()

    class Meta:
        model = Company
        fields = [
            "company_name",
            "industry",
            "is_active",
            "status",
        ]

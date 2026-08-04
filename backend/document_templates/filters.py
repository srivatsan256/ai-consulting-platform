import django_filters

from .models import DocumentTemplate


class DocumentTemplateFilter(django_filters.FilterSet):

    category = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    project = django_filters.NumberFilter()

    is_active = django_filters.BooleanFilter()

    class Meta:
        model = DocumentTemplate
        fields = [
            "category",
            "project",
            "is_active",
        ]

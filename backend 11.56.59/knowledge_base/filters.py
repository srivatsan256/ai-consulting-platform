import django_filters

from .models import KnowledgeBase


class KnowledgeBaseFilter(django_filters.FilterSet):

    category = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    project = django_filters.NumberFilter()

    is_published = django_filters.BooleanFilter()

    class Meta:
        model = KnowledgeBase
        fields = [
            "category",
            "project",
            "is_published",
        ]

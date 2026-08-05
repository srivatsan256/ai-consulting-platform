import django_filters
from .models import Document


class DocumentFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    document_type = django_filters.CharFilter(lookup_expr="iexact")

    status = django_filters.CharFilter(lookup_expr="iexact")

    created_by = django_filters.NumberFilter()

    class Meta:
        model = Document
        fields = [
            "project",
            "document_type",
            "status",
            "created_by",
        ]

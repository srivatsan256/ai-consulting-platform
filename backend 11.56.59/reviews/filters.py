import django_filters

from .models import Review


class ReviewFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    status = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    review_type = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    reviewer = django_filters.NumberFilter()

    rating = django_filters.NumberFilter()

    class Meta:
        model = Review
        fields = [
            "project",
            "status",
            "review_type",
            "reviewer",
            "rating",
        ]

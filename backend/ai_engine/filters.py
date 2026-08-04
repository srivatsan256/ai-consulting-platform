import django_filters

from .models import AIAssessment


class AIAssessmentFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    status = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    overall_score = django_filters.NumberFilter()

    class Meta:
        model = AIAssessment
        fields = [
            "project",
            "status",
            "overall_score",
        ]

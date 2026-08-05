import django_filters

from .models import Workflow


class WorkflowFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    status = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    class Meta:
        model = Workflow
        fields = [
            "project",
            "status",
        ]

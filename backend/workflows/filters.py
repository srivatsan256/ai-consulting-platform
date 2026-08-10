import django_filters

from .models import Workflow, WorkflowExecution, WorkflowHistory


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


class WorkflowExecutionFilter(django_filters.FilterSet):

    workflow = django_filters.NumberFilter()

    status = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    entity_type = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    class Meta:
        model = WorkflowExecution
        fields = ["workflow", "status", "entity_type"]


class WorkflowHistoryFilter(django_filters.FilterSet):

    workflow = django_filters.NumberFilter()

    workflow_execution = django_filters.NumberFilter()

    event_type = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    actor = django_filters.NumberFilter()

    class Meta:
        model = WorkflowHistory
        fields = ["workflow", "workflow_execution", "event_type", "actor"]

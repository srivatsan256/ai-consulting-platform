import django_filters

from .models import Approval


class ApprovalFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    entity_type = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    status = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    assigned_to = django_filters.NumberFilter()

    requested_by = django_filters.NumberFilter()

    class Meta:
        model = Approval
        fields = [
            "project",
            "entity_type",
            "status",
            "assigned_to",
            "requested_by",
        ]

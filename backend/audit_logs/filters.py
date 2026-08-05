import django_filters

from .models import AuditLog


class AuditLogFilter(django_filters.FilterSet):

    user = django_filters.NumberFilter()

    action = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    entity_type = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    timestamp_after = django_filters.IsoDateTimeFilter(
        field_name="timestamp",
        lookup_expr="gte",
    )

    timestamp_before = django_filters.IsoDateTimeFilter(
        field_name="timestamp",
        lookup_expr="lte",
    )

    class Meta:
        model = AuditLog
        fields = [
            "user",
            "action",
            "entity_type",
            "timestamp_after",
            "timestamp_before",
        ]

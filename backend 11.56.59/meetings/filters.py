import django_filters

from .models import Meeting


class MeetingFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    status = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    organizer = django_filters.NumberFilter()

    start_after = django_filters.IsoDateTimeFilter(
        field_name="start_time",
        lookup_expr="gte",
    )

    start_before = django_filters.IsoDateTimeFilter(
        field_name="start_time",
        lookup_expr="lte",
    )

    class Meta:
        model = Meeting
        fields = [
            "project",
            "status",
            "organizer",
            "start_after",
            "start_before",
        ]

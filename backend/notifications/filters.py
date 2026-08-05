import django_filters

from .models import Notification


class NotificationFilter(django_filters.FilterSet):

    notification_type = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    category = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    is_read = django_filters.BooleanFilter()

    class Meta:
        model = Notification
        fields = [
            "notification_type",
            "category",
            "is_read",
        ]

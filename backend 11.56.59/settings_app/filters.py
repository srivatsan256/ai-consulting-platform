import django_filters

from .models import SystemSetting


class SystemSettingFilter(django_filters.FilterSet):

    category = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    is_sensitive = django_filters.BooleanFilter()

    class Meta:
        model = SystemSetting
        fields = [
            "category",
            "is_sensitive",
        ]

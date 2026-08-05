import django_filters

from .models import Deployment


class DeploymentFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    environment = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    status = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    class Meta:
        model = Deployment
        fields = [
            "project",
            "environment",
            "status",
        ]

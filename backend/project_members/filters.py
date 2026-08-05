import django_filters
from .models import ProjectMember


class ProjectMemberFilter(django_filters.FilterSet):

    project = django_filters.NumberFilter()

    user = django_filters.NumberFilter()

    role = django_filters.NumberFilter()

    is_active = django_filters.BooleanFilter()

    class Meta:
        model = ProjectMember
        fields = [
            "project",
            "user",
            "role",
            "is_active",
        ]

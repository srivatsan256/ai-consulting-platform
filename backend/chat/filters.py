import django_filters

from .models import Conversation


class ConversationFilter(django_filters.FilterSet):

    conversation_type = django_filters.CharFilter(
        lookup_expr="iexact",
    )

    project = django_filters.NumberFilter()

    class Meta:
        model = Conversation
        fields = [
            "conversation_type",
            "project",
        ]

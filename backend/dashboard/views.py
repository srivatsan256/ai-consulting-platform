from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import DashboardWidget
from .serializers import DashboardWidgetSerializer
from .filters import DashboardWidgetFilter


class DashboardWidgetViewSet(viewsets.ModelViewSet):

    serializer_class = DashboardWidgetSerializer

    queryset = DashboardWidget.objects.select_related(
        "owner",
        "project",
    )

    filterset_class = DashboardWidgetFilter

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DashboardWidget.objects.filter(
            owner=self.request.user,
        ).select_related("owner", "project")

    ordering_fields = [
        "position",
        "created_at",
    ]

    ordering = ["position"]

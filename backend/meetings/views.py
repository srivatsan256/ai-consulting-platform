from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Meeting, MeetingMinutes
from .serializers import MeetingSerializer, MeetingMinutesSerializer
from .filters import MeetingFilter
from core.tenant_scoping import TenantScopedViewSetMixin


class MeetingViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = MeetingSerializer

    queryset = Meeting.objects.select_related(
        "project",
        "organizer",
    ).prefetch_related("participants")

    filterset_class = MeetingFilter

    search_fields = [
        "title",
        "description",
    ]

    ordering_fields = [
        "start_time",
        "created_at",
        "status",
    ]

    ordering = ["-start_time"]

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(
            participants=self.request.user,
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        meeting = self.get_object()
        meeting.status = "completed"
        meeting.save()
        return Response({"message": "Meeting marked as completed."})

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        meeting = self.get_object()
        meeting.status = "cancelled"
        meeting.save()
        return Response({"message": "Meeting cancelled."})

    @action(detail=True, methods=["get", "post"])
    def minutes(self, request, pk=None):
        meeting = self.get_object()

        if request.method == "GET":
            try:
                minutes = meeting.minutes
                serializer = MeetingMinutesSerializer(minutes)
                return Response(serializer.data)
            except MeetingMinutes.DoesNotExist:
                return Response(None)

        serializer = MeetingMinutesSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(meeting=meeting)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

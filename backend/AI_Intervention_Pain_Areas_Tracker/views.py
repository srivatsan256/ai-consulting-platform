from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend # type: ignore

from .models import AIInterventionPainArea
from .serializers import AIInterventionPainAreaSerializer


class AIInterventionPainAreaViewSet(viewsets.ModelViewSet):
    queryset = AIInterventionPainArea.objects.all()
    serializer_class = AIInterventionPainAreaSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "priority", "feasibility", "department"]
    search_fields = ["process_activity", "pain_area", "ai_intervention", "owner", "department", "remarks"]
    ordering_fields = ["date", "created_at", "updated_at", "priority", "status"]
    ordering = ["-date", "-created_at"]

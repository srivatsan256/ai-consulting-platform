from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import DocumentTemplate
from .serializers import DocumentTemplateSerializer
from .filters import DocumentTemplateFilter


class DocumentTemplateViewSet(viewsets.ModelViewSet):

    serializer_class = DocumentTemplateSerializer

    queryset = DocumentTemplate.objects.select_related(
        "project",
        "created_by",
    )

    filterset_class = DocumentTemplateFilter

    search_fields = [
        "name",
        "description",
    ]

    ordering_fields = [
        "name",
        "created_at",
        "updated_at",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

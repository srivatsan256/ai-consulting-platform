import csv
import io

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend # type: ignore

from .models import AIInterventionPainArea
from .serializers import AIInterventionPainAreaSerializer

WRITABLE_FIELDS = {
    "date",
    "department",
    "process_activity",
    "pain_area",
    "current_method",
    "frequency",
    "time_spent_hrs",
    "impact_area",
    "ai_intervention",
    "expected_benefit",
    "priority",
    "feasibility",
    "owner",
    "target_date",
    "status",
    "remarks",
}


class AIInterventionPainAreaViewSet(viewsets.ModelViewSet):
    queryset = AIInterventionPainArea.objects.all()
    serializer_class = AIInterventionPainAreaSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "priority", "feasibility", "department"]
    search_fields = ["process_activity", "pain_area", "ai_intervention", "owner", "department", "remarks"]
    ordering_fields = ["date", "created_at", "updated_at", "priority", "status"]
    ordering = ["-date", "-created_at"]

    @action(detail=False, methods=["post"], url_path="import_csv", url_name="import_csv")
    def import_csv(self, request):
        """
        Import pain area records from an uploaded CSV file.

        POST multipart form with a ``file`` field containing a CSV whose
        columns match the writable serializer fields. Returns a summary:
        ``{"inserted": n, "skipped": n, "warnings": [...]}``
        """
        file_obj = request.FILES.get("file")
        if file_obj is None:
            return Response(
                {"detail": "No CSV file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw = file_obj.read().decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(raw))

        inserted = 0
        skipped = 0
        warnings = []

        for index, row in enumerate(reader, start=1):
            if row is None:
                continue

            data = {}
            for field, value in row.items():
                key = (field or "").strip()
                if not key or key not in WRITABLE_FIELDS:
                    continue
                val = value.strip() if isinstance(value, str) else value
                if val == "":
                    continue
                data[key] = val

            if not data:
                continue

            serializer = AIInterventionPainAreaSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                inserted += 1
            else:
                skipped += 1
                warnings.append({"row": index, "error": serializer.errors})

        return Response(
            {"inserted": inserted, "skipped": skipped, "warnings": warnings},
            status=status.HTTP_200_OK,
        )

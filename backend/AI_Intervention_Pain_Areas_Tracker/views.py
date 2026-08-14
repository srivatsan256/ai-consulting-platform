import csv
import datetime
import io
import re
import uuid

from django.db import connection, transaction
from django.db.utils import OperationalError, ProgrammingError
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend # type: ignore

from .models import AIInterventionPainArea
from .serializers import AIInterventionPainAreaSerializer

STAGING_TABLE = "ai_pain_area_csv_staging"
STAGING_FUNCTION = "process_pain_area_csv_import"
STAGING_COLUMNS = [
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
]

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_IMPORT_ROWS = 5000

DATE_FIELDS = {"date", "target_date"}
CHOICE_FIELDS = {"priority", "feasibility", "status"}

CHOICES = {
    "priority": ["High", "Medium", "Low"],
    "feasibility": ["High", "Medium", "Low"],
    "status": ["Open", "In Progress", "Completed", "On Hold", "Cancelled"],
}

# Header names are slugified (lowercased, non-alphanumerics dropped) and
# matched against these aliases so real-world CSVs (Excel exports, spaced or
# title-cased headers) import cleanly.
HEADER_ALIASES = {
    "date": "date",
    "targetdate": "target_date",
    "target_date": "target_date",
    "department": "department",
    "processactivity": "process_activity",
    "process_activity": "process_activity",
    "painarea": "pain_area",
    "pain_area": "pain_area",
    "painareaproblem": "pain_area",
    "painareaproblemstatement": "pain_area",
    "currentmethod": "current_method",
    "current_method": "current_method",
    "frequency": "frequency",
    "timespent": "time_spent_hrs",
    "timespenthrs": "time_spent_hrs",
    "time_spent": "time_spent_hrs",
    "time_spent_hrs": "time_spent_hrs",
    "timespentmonthhrs": "time_spent_hrs",
    "timespentpermonthhrs": "time_spent_hrs",
    "hrs": "time_spent_hrs",
    "hours": "time_spent_hrs",
    "impactarea": "impact_area",
    "impact_area": "impact_area",
    "aiintervention": "ai_intervention",
    "ai_intervention": "ai_intervention",
    "aiinterventionrequired": "ai_intervention",
    "expectedbenefit": "expected_benefit",
    "expected_benefit": "expected_benefit",
    "priority": "priority",
    "feasibility": "feasibility",
    "owner": "owner",
    "status": "status",
    "remarks": "remarks",
    "notes": "remarks",
}

EXCEL_EPOCH = datetime.date(1899, 12, 30)

DATE_FORMATS = (
    "%d/%m/%Y",
    "%d/%m/%y",
    "%d-%m-%Y",
    "%d-%m-%y",
    "%d.%m.%Y",
    "%d.%m.%y",
    "%Y/%m/%d",
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%m/%d/%y",
    "%d %b %Y",
    "%d %b %y",
    "%d-%b-%Y",
    "%d-%b-%y",
    "%b %d, %Y",
    "%b %d, %y",
)


def _slugify_header(name):
    return re.sub(r"[^a-z0-9]+", "", (name or "").lower().strip())


def _build_header_map(fieldnames):
    mapping = {}
    for header in fieldnames or []:
        field = HEADER_ALIASES.get(_slugify_header(header))
        if field:
            mapping[header] = field
    return mapping


def _detect_delimiter(raw):
    first_line = raw.splitlines()[0] if raw.splitlines() else ""
    counts = {
        ",": first_line.count(","),
        ";": first_line.count(";"),
        "\t": first_line.count("\t"),
        "|": first_line.count("|"),
    }
    best = max(counts, key=counts.get) # type: ignore
    return best if counts[best] > 0 else ","


def _parse_flexible_date(value):
    s = str(value).strip()
    if not s:
        return None
    # Excel serial date numbers (days since 1899-12-30), e.g. 45800 or 45800.5.
    if re.fullmatch(r"\d{4,6}(?:\.\d+)?", s):
        try:
            serial = int(float(s))
            return EXCEL_EPOCH + datetime.timedelta(days=serial)
        except (OverflowError, ValueError):
            return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _normalize_choice(field, value):
    v = str(value).strip()
    for canonical in CHOICES[field]:
        if v.lower() == canonical.lower():
            return canonical
    return v  # let the serializer report the invalid choice


def _normalize_row(row, header_map):
    data = {}
    for raw_header, value in row.items():
        field = header_map.get(raw_header)
        if not field:
            continue
        val = value.strip() if isinstance(value, str) else value
        if val == "":
            continue
        if field in DATE_FIELDS:
            parsed = _parse_flexible_date(val)
            if parsed is not None:
                data[field] = parsed.isoformat()
            else:
                data[field] = val  # serializer reports a clear date error
        elif field in CHOICE_FIELDS:
            data[field] = _normalize_choice(field, val)
        elif field == "time_spent_hrs":
            data[field] = val.replace(",", "")
        else:
            data[field] = val
    return data


class AIInterventionPainAreaViewSet(viewsets.ModelViewSet):
    queryset = AIInterventionPainArea.objects.all()
    serializer_class = AIInterventionPainAreaSerializer
    permission_classes = [IsAuthenticated]
    # The dashboard/table renders all records; no page size cap.
    pagination_class = None

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "priority", "feasibility", "department"]
    search_fields = ["process_activity", "pain_area", "ai_intervention", "owner", "department", "remarks"]
    ordering_fields = ["date", "created_at", "updated_at", "priority", "status"]
    ordering = ["-date", "-created_at"]

    @action(detail=False, methods=["post"], url_path="upload-csv", url_name="upload-csv")
    def upload_csv(self, request):
        """
        Import pain area records from an uploaded CSV file.

        POST multipart form with a ``file`` field containing a CSV whose
        columns match the writable serializer fields.

        Flow: Django validates each row, stages the valid rows into
        ``ai_pain_area_csv_staging`` and invokes the PostgreSQL function
        ``process_pain_area_csv_import`` which transforms + inserts the final
        records and purges the batch. Falls back to direct ORM inserts when the
        staging pipeline is unavailable (e.g. local SQLite).

        Returns: ``{"inserted": n, "skipped": n, "warnings": [...]}``
        """
        file_obj = request.FILES.get("file")
        if file_obj is None:
            return Response(
                {"detail": "No CSV file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if file_obj.size and file_obj.size > MAX_UPLOAD_SIZE:
            return Response(
                {"detail": "CSV file is too large (max 10 MB)."},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

        try:
            raw = file_obj.read().decode("utf-8-sig")
        except UnicodeDecodeError:
            return Response(
                {"detail": "CSV file must be UTF-8 encoded."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        delimiter = _detect_delimiter(raw)
        reader = csv.DictReader(io.StringIO(raw), delimiter=delimiter)
        header_map = _build_header_map(reader.fieldnames)

        skipped = 0
        warnings = []
        rows = []
        data_rows = 0

        for index, row in enumerate(reader, start=1):
            if row is None:
                continue
            data = _normalize_row(row, header_map)
            if not data:
                continue
            data_rows += 1
            if data_rows > MAX_IMPORT_ROWS:
                return Response(
                    {"detail": f"Too many rows (max {MAX_IMPORT_ROWS})."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = AIInterventionPainAreaSerializer(data=data)
            if serializer.is_valid():
                rows.append((index, serializer.validated_data))
            else:
                skipped += 1
                warnings.append({"row": index, "error": serializer.errors})

        if data_rows == 0:
            return Response(
                {"detail": "CSV is empty or contains no data rows."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        inserted = 0
        if rows:
            try:
                inserted, fn_skipped, fn_warnings = self._run_staging_pipeline(rows)
                skipped += fn_skipped
                warnings.extend(fn_warnings)
            except (ProgrammingError, OperationalError):
                for _, validated in rows:
                    AIInterventionPainArea.objects.create(**validated)
                    inserted += 1

        return Response(
            {"inserted": inserted, "skipped": skipped, "warnings": warnings},
            status=status.HTTP_200_OK,
        )

    def _pg_pipeline_available(self):
        if connection.vendor != "postgresql":
            return False
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT to_regprocedure(%s);",
                    [f"{STAGING_FUNCTION}(uuid)"],
                )
                return cursor.fetchone()[0] is not None
        except Exception:
            return False

    def _run_staging_pipeline(self, rows):
        if not self._pg_pipeline_available():
            raise ProgrammingError("PostgreSQL staging pipeline is not available.")

        batch_id = uuid.uuid4()
        placeholders = ", ".join(["%s"] * (len(STAGING_COLUMNS) + 2))
        columns = ", ".join(["batch_id", "row_number", *STAGING_COLUMNS])
        insert_sql = (
            f"INSERT INTO {STAGING_TABLE} ({columns}) VALUES ({placeholders})"
        )

        payload = [
            (
                batch_id,
                row_number,
                *(validated.get(col) for col in STAGING_COLUMNS),
            )
            for row_number, validated in rows
        ]

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.executemany(insert_sql, payload)
                cursor.execute(
                    f"SELECT * FROM {STAGING_FUNCTION}(%s) "
                    "AS (inserted bigint, skipped bigint, warnings text[]);",
                    [batch_id],
                )
                inserted, skipped, fn_warnings = cursor.fetchone()

        return inserted, skipped, list(fn_warnings or [])

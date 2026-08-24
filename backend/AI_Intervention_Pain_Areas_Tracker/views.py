import csv
import datetime
import io
import re
import uuid

from django.db import connection, transaction
from django.db.models import Count, Sum
from django.db.utils import OperationalError, ProgrammingError
from django.http import HttpResponse
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend # type: ignore

from .models import AIInterventionPainArea
from .serializers import AIInterventionPainAreaSerializer
from .report_generation import REPORT_TYPES, build_report_data, export_report
from .scoring import score_from_time_spent, score_from_feasibility, needs_input as _needs_input

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

    @action(detail=False, methods=["get"], url_path="reports", url_name="reports")
    def reports(self, request):
        """List available executive reports and their computed data."""
        records = list(self.get_queryset())
        data = build_report_data(records)
        return Response(
            {
                "report_types": [
                    {"key": key, **meta} for key, meta in REPORT_TYPES.items()
                ],
                "data": data,
            }
        )

    @action(
        detail=False,
        methods=["get"],
        url_path=r"reports/(?P<report_type>[^/.]+)/export",
        url_name="report-export",
    )
    def export_report(self, request, report_type=None):
        """Download a report as PDF or Excel.

        GET /reports/<report_type>/export/?file_format=pdf|xlsx
        """
        if report_type not in REPORT_TYPES:
            return Response(
                {"detail": f"Unknown report type '{report_type}'."},
                status=status.HTTP_404_NOT_FOUND,
            )
        fmt = (request.query_params.get("file_format") or "pdf").lower()
        if fmt not in ("pdf", "xlsx"):
            return Response(
                {"detail": "file_format must be 'pdf' or 'xlsx'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        records = list(self.get_queryset())
        mimetype, extension, payload = export_report(report_type, fmt, records)
        filename = f"{report_type}-{datetime.date.today().isoformat()}.{extension}"
        response = HttpResponse(payload, content_type=mimetype)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

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

    @action(detail=False, methods=["get"], url_path="audit", url_name="audit")
    def audit(self, request):
        """Return a structured data-quality audit of the pain areas tracker.

        Response shape
        --------------
        {
          "column_inventory": [{"field": str, "type": str, "filled": int, "missing": int}],
          "total_records": int,
          "needs_input_count": int,
          "needs_input_pct": float,
          "flagged_rows": [{"id": int, "process_activity": str, "missing_fields": [str]}],
          "quadrant_distribution": {"Quick Win": int, "Major Project": int,
                                    "Fill In": int, "Reconsider": int, "Needs Input": int},
          "executive_summary": str,
          "primary_blocker": str | null,
        }
        """
        records = list(self.get_queryset())
        total = len(records)

        # ── Column inventory ──────────────────────────────────────────────────
        AUDITED_FIELDS = [
            ("time_spent_hrs", "float"),
            ("priority", "choice"),
            ("feasibility", "choice"),
            ("department", "text"),
            ("process_activity", "text"),
            ("owner", "text"),
            ("target_date", "date"),
            ("status", "choice"),
        ]
        column_inventory = []
        for field, ftype in AUDITED_FIELDS:
            filled = sum(1 for r in records if getattr(r, field, None) not in (None, ""))
            column_inventory.append({
                "field": field, "type": ftype,
                "filled": filled, "missing": total - filled,
            })

        # ── Row-level gap analysis ─────────────────────────────────────────────
        CRITICAL_FIELDS = ["time_spent_hrs", "priority", "feasibility"]
        flagged_rows = []
        needs_input_count = 0
        for r in records:
            missing = [f for f in CRITICAL_FIELDS if getattr(r, f, None) in (None, "")]
            if missing:
                flagged_rows.append({
                    "id": r.id,
                    "process_activity": r.process_activity or "(unnamed)",
                    "missing_fields": missing,
                })
            if _needs_input(r):
                needs_input_count += 1

        needs_input_pct = round(needs_input_count / total * 100, 1) if total else 0.0

        # ── Quadrant distribution ─────────────────────────────────────────────
        from .scoring import quadrant_from_scores
        quadrant_counts = {
            "Quick Win": 0, "Major Project": 0,
            "Fill In": 0, "Reconsider": 0, "Needs Input": 0,
        }
        for r in records:
            impact = score_from_time_spent(r.time_spent_hrs)
            feasibility = score_from_feasibility(r.feasibility)
            q = quadrant_from_scores(impact, feasibility)
            if q in quadrant_counts:
                quadrant_counts[q] += 1

        scoreable = total - needs_input_count
        qw = quadrant_counts["Quick Win"]
        mp = quadrant_counts["Major Project"]
        fi = quadrant_counts["Fill In"]
        rc = quadrant_counts["Reconsider"]

        # ── Executive summary ─────────────────────────────────────────────────
        if total == 0:
            exec_summary = "No records found in the tracker."
            blocker = None
        elif needs_input_pct > 50:
            exec_summary = (
                f"Of {total} initiatives, {scoreable} can be scored today "
                f"({qw} Quick Win, {mp} Major Project, {fi} Fill In, {rc} Reconsider); "
                f"{needs_input_count} show \u2018Needs Input\u2019 because Time Spent / Month "
                f"was never filled in. Next step: close the data gap."
            )
            blocker = (
                f"{needs_input_count} of {total} items ({needs_input_pct}%) are missing "
                "\u2018Time Spent / Month\u2019. Fill this field to unlock full prioritisation."
            )
        else:
            exec_summary = (
                f"Of {total} initiatives, {qw} are Quick Wins, {mp} are Major Projects, "
                f"{fi} are Fill Ins, and {rc} should be Reconsidered. "
                f"{needs_input_count} still need data to be scored."
            )
            blocker = (
                f"{needs_input_count} records are missing \u2018Time Spent / Month\u2019."
                if needs_input_count else None
            )

        return Response({
            "column_inventory": column_inventory,
            "total_records": total,
            "needs_input_count": needs_input_count,
            "needs_input_pct": needs_input_pct,
            "flagged_rows": flagged_rows,
            "quadrant_distribution": quadrant_counts,
            "executive_summary": exec_summary,
            "primary_blocker": blocker,
        })


def classify_phase(quadrant, total_score):
    """
    Classify an opportunity into a roadmap phase based on Quadrant and Total Score.

    Total Score (impact + feasibility + priority) ranges from 3 to 9.
    Classification rules (normalized to the existing 3-9 scale):
    - Phase 1 "Quick Wins": Quadrant = Quick Win AND Total Score >= 7
    - Phase 2 "Major Projects": Quadrant = Major Project
    - Phase 3 "Strategic Initiatives": Total Score between 4 and 6
    - Phase 4 "Future Consideration": Quadrant = Reconsider (maps to Revisit)
    """
    # Phase 1: Quick Wins - Quick Win quadrant AND high total score
    if quadrant == "Quick Win" and total_score >= 7:
        return 1
    # Phase 2: Major Projects - Quadrant = Major Project
    # Note: "Major Project" quadrant may need to be set on records via API/admin
    if quadrant == "Major Project":
        return 2
    # Phase 3: Strategic Initiatives - Total Score between 4 and 6
    if 4 <= total_score <= 6:
        return 3
    # Phase 4: Future Consideration - Reconsider quadrant maps to Revisit
    if quadrant in ("Revisit", "Reconsider"):
        return 4
    return None


class RoadmapViewSet(viewsets.ViewSet):
    """
    API endpoint that returns opportunities grouped by roadmap phase,
    plus summary statistics.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = []  # Will use default from setting

    def list(self, request):
        from .models import AIInterventionPainArea
        from .serializers import AIInterventionPainAreaSerializer

        # Fetch all records
        records = AIInterventionPainArea.objects.all()
        serializer = AIInterventionPainAreaSerializer(records, many=True)
        data = serializer.data

        # Classify each record into a phase
        phases = {1: [], 2: [], 3: [], 4: []}
        phase_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        total_hours_saved = 0

        for record in data:
            quadrant = record.get("quadrant", "")
            total_score = record.get("total_score", 0) or 0
            hours_saved = record.get("time_spent_hrs") or 0

            total_hours_saved += hours_saved or 0

            phase = classify_phase(quadrant, total_score)
            if phase is not None:
                phases[phase].append(record)
                phase_counts[phase] += 1

        # Build summary
        summary = {
            "total_projects": sum(phase_counts.values()),
            "phase_counts": phase_counts,
            "estimated_total_hours_saved": round(total_hours_saved, 2),
        }

        # Build response
        response_data = {
            "phases": {
                1: {
                    "name": "Quick Wins",
                    "description": "Quadrant = Quick Win AND Total Score >= 7",
                    "projects": phases[1],
                    "count": phase_counts[1],
                },
                2: {
                    "name": "Major Projects",
                    "description": "Quadrant = Major Project",
                    "projects": phases[2],
                    "count": phase_counts[2],
                },
                3: {
                    "name": "Strategic Initiatives",
                    "description": "Total Score between 4 and 6",
                    "projects": phases[3],
                    "count": phase_counts[3],
                },
                4: {
                    "name": "Future Consideration",
                    "description": "Quadrant = Reconsider (maps to Revisit)",
                    "projects": phases[4],
                    "count": phase_counts[4],
                },
            },
            "summary": summary,
        }

        return Response(response_data)


class AssistantView(viewsets.ViewSet):
    """
    Rule-based AI assistant that answers natural-language questions about the
    AI pain area portfolio by converting them into filtered queries. No LLM.
    """
    permission_classes = [IsAuthenticated]

    def create(self, request):
        from .assistant import answer as assistant_answer

        question = request.data.get("question", "")
        result = assistant_answer(question)
        return Response(result, status=status.HTTP_200_OK)


class DepartmentStatsViewSet(viewsets.ViewSet):
    """
    Department-level aggregates for the AI pain area portfolio.

    Uses ORM aggregations for directly-stored fields (count, hours, status and
    priority distributions). Derived scoring fields (impact_score, total_score,
    quadrant) are computed per record via the shared scoring helpers, then
    grouped by department.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        from .models import AIInterventionPainArea
        from .scoring import (
            score_from_priority,
            score_from_feasibility,
            score_from_time_spent,
            quadrant_from_scores,
        )

        rows = (
            AIInterventionPainArea.objects.values("department")
            .annotate(count=Count("id"), total_hours=Sum("time_spent_hrs"))
            .order_by("-total_hours")
        )

        stats = {}
        for r in AIInterventionPainArea.objects.all():
            dept = r.department or "Unknown"
            impact = score_from_time_spent(r.time_spent_hrs)
            feasibility = score_from_feasibility(r.feasibility)
            priority = score_from_priority(r.priority)
            total = (impact or 0) + (feasibility or 0) + (priority or 0)
            q = quadrant_from_scores(impact, feasibility)
            d = stats.setdefault(
                dept,
                {
                    "impact_sum": 0,
                    "total_sum": 0,
                    "quadrants": {"Quick Win": 0, "Major Project": 0, "Fill In": 0, "Reconsider": 0, "Needs Input": 0},
                    "status": {"Open": 0, "In Progress": 0, "Completed": 0, "On Hold": 0, "Cancelled": 0},
                    "priority": {"High": 0, "Medium": 0, "Low": 0},
                    "processes": [],
                },
            )
            d["impact_sum"] += impact or 0
            d["total_sum"] += total
            if q in d["quadrants"]:
                d["quadrants"][q] += 1
            if r.status in d["status"]:
                d["status"][r.status] += 1
            if r.priority in d["priority"]:
                d["priority"][r.priority] += 1
            d["processes"].append(
                {
                    "process": r.process_activity,
                    "hours": r.time_spent_hrs,
                    "score": total,
                    "recommendation": r.ai_intervention,
                }
            )

        result = []
        for row in rows:
            dept = row["department"] or "Unknown"
            d = stats.get(dept, {})
            count = row["count"] or 0
            procs = sorted(
                d.get("processes", []),
                key=lambda p: (p["score"] or 0),
                reverse=True,
            )[:5]
            avg_impact = round(d["impact_sum"] / count, 2) if count else 0
            avg_total = round(d["total_sum"] / count, 2) if count else 0
            result.append(
                {
                    "name": dept,
                    "id": dept,
                    "opportunities": count,
                    "total_hours": round(row["total_hours"] or 0, 2),
                    "avg_impact": avg_impact,
                    "avg_total_score": avg_total,
                    "quick_wins": d.get("quadrants", {}).get("Quick Win", 0),
                    "major_projects": d.get("quadrants", {}).get("Major Project", 0),
                    "quadrants": d.get("quadrants", {}),
                    "status": d.get("status", {}),
                    "priority": d.get("priority", {}),
                    "top_processes": procs,
                }
            )
        return Response({"departments": result})

    def retrieve(self, request, pk=None):
        from .models import AIInterventionPainArea
        from .scoring import (
            score_from_priority,
            score_from_time_spent,
            quadrant_from_scores,
        )

        all_rows = self.list(request).data["departments"]
        dept = next((d for d in all_rows if d["id"] == pk), None)
        if dept is None:
            return Response({"detail": "Department not found."}, status=404)
        return Response({"department": dept})

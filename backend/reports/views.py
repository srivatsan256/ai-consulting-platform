from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import Report
from .serializers import ReportSerializer
from .filters import ReportFilter
from core.ai_service import generate_verification_report, keyword_extraction, language_analysis
from core.rule_engine import validate_document


class ReportViewSet(viewsets.ModelViewSet):

    serializer_class = ReportSerializer

    queryset = Report.objects.select_related(
        "project",
        "created_by",
    )

    filterset_class = ReportFilter

    search_fields = [
        "title",
        "content",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "report_type",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        report = self.get_object()
        report.status = "published"
        report.published_at = timezone.now()
        report.save(update_fields=["status", "published_at"])
        return Response({"message": "Report published."})

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        report = self.get_object()
        report.status = "archived"
        report.save(update_fields=["status"])
        return Response({"message": "Report archived."})

    @action(detail=True, methods=["post"])
    def generate_verification(self, request, pk=None):
        report = self.get_object()
        custom_rules = request.data.get("rules", None)
        rule_results = validate_document(report.content, custom_rules)
        try:
            ai_result = generate_verification_report(
                report.content,
                rules=[r["name"] for r in rule_results["results"]],
            )
            report.content = (
                f"{report.content}\n\n--- AI VERIFICATION REPORT ---\n\n"
                f"{ai_result['report']}"
            )
            report.save(update_fields=["content"])
            return Response({
                "message": "Verification report generated.",
                "compliance_score": rule_results["compliance_score"],
                "rule_results": rule_results["results"],
                "ai_report": ai_result["report"],
            })
        except Exception as e:
            return Response({
                "message": "Rule-based verification completed.",
                "compliance_score": rule_results["compliance_score"],
                "rule_results": rule_results["results"],
                "ai_report": None,
                "ai_error": str(e),
            })

    @action(detail=True, methods=["post"])
    def extract_keywords(self, request, pk=None):
        report = self.get_object()
        text = request.data.get("text", report.content)
        try:
            keywords = keyword_extraction(text)
            return Response({
                "keywords": keywords,
                "count": len(keywords),
            })
        except Exception as e:
            return Response(
                {"error": f"Keyword extraction failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def language_check(self, request, pk=None):
        report = self.get_object()
        text = request.data.get("text", report.content)
        try:
            analysis = language_analysis(text)
            return Response(analysis)
        except Exception as e:
            return Response(
                {"error": f"Language analysis failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

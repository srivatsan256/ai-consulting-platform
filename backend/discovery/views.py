from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Discovery, DiscoveryText, DiscoveryDocument
from .serializers import DiscoverySerializer
from .filters import DiscoveryFilter
from core.ai_service import analyze_proposal, generate_project_proposal
from core.document_processor import extract_text_from_uploaded_file
from core.vector_store import add_document as add_to_vector_store
from core.tenant_scoping import TenantScopedViewSetMixin


class DiscoveryViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = DiscoverySerializer
    permission_classes = [IsAuthenticated]

    queryset = Discovery.objects.select_related(
        "project",
        "created_by",
        "updated_by",
    )

    filterset_class = DiscoveryFilter

    search_fields = [
        "project__project_name",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "status",
    ]

    ordering = [
        "-created_at"
    ]

    def _get_discovery_text(self, discovery):
        try:
            text_content = discovery.text_content
            fields = [
                "executive_summary", "business_problem", "business_goal",
                "current_process", "pain_points", "opportunities",
                "functional_requirements", "non_functional_requirements",
                "risks", "dependencies", "success_criteria", "expected_roi",
                "stakeholders", "departments", "users", "assumptions",
                "constraints", "additional_notes",
            ]
            parts = []
            for field in fields:
                val = getattr(text_content, field, "")
                if val:
                    parts.append(f"{field.replace('_', ' ').title()}: {val}")
            return "\n".join(parts)
        except DiscoveryText.DoesNotExist:
            return ""

    def _get_discovery_pdf_text(self, discovery):
        try:
            doc = discovery.document
            return doc.extracted_text or ""
        except DiscoveryDocument.DoesNotExist:
            return ""

    def _extract_pdf_text(self, discovery):
        try:
            doc = discovery.document
            if doc.uploaded_file and not doc.extracted_text:
                result = extract_text_from_uploaded_file(doc.uploaded_file)
                doc.extracted_text = result.get("text", "")
                doc.total_pages = result.get("total_pages", 0)
                doc.save(update_fields=["extracted_text", "total_pages"])
                return doc.extracted_text
            return doc.extracted_text or ""
        except DiscoveryDocument.DoesNotExist:
            return ""

    def _calculate_completeness(self, discovery):
        if discovery.input_type == "text":
            try:
                text_content = discovery.text_content
                required_fields = [
                    "business_problem", "business_goal",
                    "current_process", "pain_points",
                ]
                optional_fields = [
                    "executive_summary", "future_process",
                    "stakeholders", "departments", "users",
                    "assumptions", "constraints", "opportunities",
                    "functional_requirements", "non_functional_requirements",
                    "risks", "dependencies", "success_criteria",
                    "expected_roi", "additional_notes",
                ]
                filled_required = sum(
                    1 for f in required_fields
                    if getattr(text_content, f, "")
                )
                filled_optional = sum(
                    1 for f in optional_fields
                    if getattr(text_content, f, "")
                )
                required_weight = 60
                optional_weight = 40
                req_score = (filled_required / len(required_fields)) * required_weight
                opt_score = (filled_optional / len(optional_fields)) * optional_weight
                return int(req_score + opt_score)
            except DiscoveryText.DoesNotExist:
                return 0
        elif discovery.input_type == "pdf":
            try:
                doc = discovery.document
                if doc.extracted_text:
                    length = len(doc.extracted_text)
                    if length > 2000:
                        return 100
                    elif length > 1000:
                        return 75
                    elif length > 500:
                        return 50
                    return 25
                return 0
            except DiscoveryDocument.DoesNotExist:
                return 0
        return 0

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        discovery = self.get_object()
        if discovery.input_type == "pdf":
            self._extract_pdf_text(discovery)
        discovery.completeness_score = self._calculate_completeness(discovery)
        discovery.save(update_fields=["completeness_score"])
        discovery.status = "submitted"
        discovery.save(update_fields=["status"])
        return Response({
            "message": "Discovery submitted successfully.",
            "completeness_score": discovery.completeness_score,
        })

    @action(detail=True, methods=["post"])
    def analyze(self, request, pk=None):
        discovery = self.get_object()
        if discovery.input_type == "pdf":
            self._extract_pdf_text(discovery)
        discovery_text = self._get_discovery_text(discovery)
        pdf_text = self._get_discovery_pdf_text(discovery)
        full_text = f"{discovery_text}\n\n{pdf_text}".strip()
        if not full_text:
            return Response(
                {"error": "No content to analyze."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            result = analyze_proposal(full_text)
            discovery.ai_processed = True
            discovery.completeness_score = self._calculate_completeness(discovery)
            discovery.save(update_fields=["ai_processed", "completeness_score"])
            add_to_vector_store(
                doc_id=f"discovery_{discovery.pk}",
                text=full_text,
                metadata={
                    "type": "discovery",
                    "project_id": discovery.project_id,
                    "status": discovery.status,
                },
            )
            return Response({
                "message": "Analysis completed.",
                "analysis": result["analysis"],
                "completeness_score": discovery.completeness_score,
                "ai_processed": True,
            })
        except Exception as e:
            return Response(
                {"error": f"AI analysis failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def generate_proposal(self, request, pk=None):
        discovery = self.get_object()
        discovery_text = self._get_discovery_text(discovery)
        pdf_text = self._get_discovery_pdf_text(discovery)
        full_text = f"{discovery_text}\n\n{pdf_text}".strip()
        if not full_text:
            return Response(
                {"error": "No content to generate proposal from."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            project_name = discovery.project.project_name
            result = generate_project_proposal(project_name, full_text)
            return Response({
                "message": "Proposal generated.",
                "proposal": result["proposal"],
                "project_name": project_name,
            })
        except Exception as e:
            return Response(
                {"error": f"Proposal generation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        discovery = self.get_object()
        discovery.status = "review"
        discovery.save(update_fields=["status"])
        return Response({"message": "Discovery moved to review."})

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        discovery = self.get_object()
        discovery.status = "approved"
        discovery.save(update_fields=["status"])
        return Response({"message": "Discovery approved."})

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        discovery = self.get_object()
        reason = request.data.get("reason", "")
        discovery.status = "rejected"
        discovery.remarks = reason
        discovery.save(update_fields=["status", "remarks"])
        return Response({"message": "Discovery rejected."})

    @action(detail=True, methods=["post"])
    def request_info(self, request, pk=None):
        discovery = self.get_object()
        message = request.data.get("message", "")
        discovery.status = "needs_info"
        discovery.remarks = message
        discovery.save(update_fields=["status", "remarks"])
        return Response({"message": "More information requested."})
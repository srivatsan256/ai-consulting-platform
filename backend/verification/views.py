import logging
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from projects.models import Project, Document, VerificationReport
from uploads.parser import extract_document_from_file
from .models import LevelModule
from .serializers import LevelModuleSerializer, LevelModuleWriteSerializer
from .level_data import TOTAL_LEVELS
from .level_verifier import verify_level_document
from .gemini_validator import gemini_validate

logger = logging.getLogger(__name__)


def _active_level(project):
    return project.current_level if project.current_level > 0 else 1


class LevelModuleViewSet(viewsets.ModelViewSet):
    """CRUD for level modules stored in the database."""
    queryset = LevelModule.objects.prefetch_related(
        "must_include_items", "recommended_items", "key_prompts_items",
        "required_doc_items", "requirement_items",
    ).all()
    serializer_class = LevelModuleSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return LevelModuleWriteSerializer
        return LevelModuleSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        level = self.request.query_params.get("level")
        if level:
            qs = qs.filter(level=int(level))
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        return qs


class VerifyAllView(APIView):
    """POST /api/projects/<uuid>/verify_all/"""

    def post(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)
        documents = project.documents.all()
        if not documents.exists():
            return Response({"detail": "No documents uploaded for this project."}, status=status.HTTP_400_BAD_REQUEST)

        results = []
        total_score = 0.0
        active_level = _active_level(project)

        for doc in documents:
            extracted = extract_document_from_file(doc.file.path)
            verification = verify_level_document(
                document_text=extracted.get("text") or doc.extracted_text or "",
                level=doc.level or active_level,
                document_data=extracted,
            )
            doc.verification_status = verification["passed"]
            doc.missing_keywords = verification["missing_requirements"]
            doc.missing_sections = verification["missing_requirements"]
            doc.save(update_fields=["verification_status", "missing_keywords", "missing_sections"])

            ai_feedback = ""
            if bool(request.data.get("use_ai", False)):
                ai_feedback = gemini_validate(
                    document_text=doc.extracted_text or "",
                    doc_type=doc.doc_type,
                    missing_keywords=verification["missing_requirements"],
                    missing_sections=verification["missing_requirements"],
                    project_context=project.objectives,
                )

            result_entry = {
                "document_id": str(doc.id),
                "doc_type": doc.doc_type,
                "ocr_used": extracted.get("ocr_used", False),
                "page_count": extracted.get("page_count", 0),
                "word_count": extracted.get("word_count", 0),
                **verification,
                "ai_feedback": ai_feedback,
            }
            results.append(result_entry)
            total_score += verification.get("score", 0)

        avg_score = round(total_score / len(results), 1) if results else 0
        current_level_docs = [doc for doc in documents if (doc.level or active_level) == active_level]
        current_level_passed = bool(current_level_docs) and all(doc.verification_status for doc in current_level_docs)

        VerificationReport.objects.update_or_create(
            project=project,
            defaults={
                "report_data": {"documents": results, "average_score": avg_score},
                "summary": f"Average readiness score: {avg_score}%",
            },
        )

        project.readiness_score = avg_score
        if current_level_passed and active_level < TOTAL_LEVELS:
            project.completed_levels = sorted(set([*project.completed_levels, active_level]))
            project.current_level = min(active_level + 1, TOTAL_LEVELS)
            project.level_scores = [*project.level_scores, {"level": active_level, "score": avg_score}]
            project.status = "PROCESSING"
            project.save(update_fields=["readiness_score", "status", "completed_levels", "current_level", "level_scores"])
        elif current_level_passed:
            project.completed_levels = sorted(set([*project.completed_levels, active_level]))
            project.level_scores = [*project.level_scores, {"level": active_level, "score": avg_score}]
            project.status = "COMPLETED"
            project.save(update_fields=["readiness_score", "status", "completed_levels", "level_scores"])
        else:
            project.status = "VERIFICATION"
            project.save(update_fields=["readiness_score", "status"])

        return Response({
            "project_id": str(project.id),
            "readiness_score": avg_score,
            "status": project.status,
            "current_level": project.current_level,
            "level_status": "PASSED" if current_level_passed else "FAILED",
            "unlock_next_level": bool(current_level_passed),
            "results": results,
        })


class ValidateDiscoveryView(APIView):
    """POST /api/projects/<uuid>/validate_discovery/"""

    def post(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)
        doc_id = request.data.get("document_id")
        if not doc_id:
            return Response({"detail": "'document_id' is required."}, status=status.HTTP_400_BAD_REQUEST)
        document = get_object_or_404(Document, pk=doc_id, project=project)
        extracted = extract_document_from_file(document.file.path)
        verification = verify_level_document(
            document_text=extracted.get("text") or document.extracted_text or "",
            level=document.level or _active_level(project),
            document_data=extracted,
        )
        document.verification_status = verification["passed"]
        document.missing_keywords = verification["missing_requirements"]
        document.missing_sections = verification["missing_requirements"]
        document.save(update_fields=["verification_status", "missing_keywords", "missing_sections"])

        ai_feedback = gemini_validate(
            document_text=document.extracted_text or "",
            doc_type=document.doc_type,
            missing_keywords=verification["missing_keywords"],
            missing_sections=verification["missing_sections"],
            project_context=project.objectives,
        )

        return Response({
            "project_id": str(project.id),
            "document_id": str(document.id),
            "ai_feedback": ai_feedback,
            "verification": verification,
            "extraction": extracted,
        })

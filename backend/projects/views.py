"""
projects/views.py
REST API views for full 5-stage consulting workflow:
  Stage 1: Project Initiation (ViewSet CRUD)
  Stage 2 & 3: Document Upload & Sequential Verification
  Stage 4: AI Processing / RAG Chatbot
  Stage 5: Final Review & Delivery (ZIP packaging)
"""
import logging

from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Project, Document, VerificationReport
from .serializers import (
    ProjectSerializer,
    DocumentSerializer,
    VerificationReportSerializer,
)
from uploads.parser import extract_document_from_file
from verification.level_data import TOTAL_LEVELS, LEVEL_REQUIREMENTS
from verification.level_verifier import verify_level_document
from services.gemini_service import GeminiService
from services.zip_service import package_project_deliverables

logger = logging.getLogger(__name__)
_gemini = GeminiService()


def _active_level(project: Project) -> int:
    return project.current_level if project.current_level > 0 else 1


class ProjectViewSet(viewsets.ModelViewSet):
    """
    Full 5-stage consulting project API.
    """
    queryset = Project.objects.all().prefetch_related("documents")
    serializer_class = ProjectSerializer

    @action(detail=True, methods=["post"], url_path="verify_all")
    def verify_all(self, request, pk=None):
        """
        Stage 3: Sequential Verification & AI Discovery
        Runs rule engine + optional Gemini analysis across all documents.
        """
        project = self.get_object()
        documents = project.documents.all()

        if not documents.exists():
            return Response(
                {"detail": "No documents uploaded for this project."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = []
        total_score = 0.0
        use_ai = bool(request.data.get("use_ai", False))
        active_level = _active_level(project)

        for doc in documents:
            extracted = extract_document_from_file(doc.file.path)
            result = verify_level_document(
                document_text=extracted.get("text") or doc.extracted_text or "",
                level=doc.level or active_level,
                document_data=extracted,
            )
            doc.verification_status = result["passed"]
            doc.missing_keywords = result["missing_requirements"]
            doc.missing_sections = result["missing_requirements"]
            doc.save(update_fields=["verification_status", "missing_keywords", "missing_sections"])

            results.append({"document_id": str(doc.id), "doc_type": doc.doc_type, "ocr_used": extracted.get("ocr_used", False), "page_count": extracted.get("page_count", 0), "word_count": extracted.get("word_count", 0), **result})
            total_score += result["score"]

        avg_score = round(total_score / len(results), 1)
        current_level_docs = [doc for doc in documents if (doc.level or active_level) == active_level]
        current_level_passed = bool(current_level_docs) and all(doc.verification_status for doc in current_level_docs)

        report_data = {"documents": results, "average_score": avg_score}
        VerificationReport.objects.update_or_create(
            project=project,
            defaults={"report_data": report_data, "summary": f"Average readiness score: {avg_score}%"},
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

        return Response(
            {
                "project_id": str(project.id),
                "readiness_score": avg_score,
                "status": project.status,
                "current_level": project.current_level,
                "level_status": "PASSED" if current_level_passed else "FAILED",
                "unlock_next_level": bool(current_level_passed),
                "results": results,
            }
        )

    @action(detail=True, methods=["get"], url_path="required_doc_status")
    def required_doc_status(self, request, pk=None):
        """Return upload/verification status for each required document at the current level."""
        project = self.get_object()
        active_level = _active_level(project)
        level_config = LEVEL_REQUIREMENTS.get(active_level, {})
        required_docs = level_config.get("required_documents", [])

        docs_for_level = project.documents.filter(level=active_level)
        uploaded_map = {}
        for doc in docs_for_level:
            uploaded_map.setdefault(doc.doc_type, []).append({
                "id": str(doc.id),
                "file_name": doc.file.name.split("/")[-1],
                "verification_status": doc.verification_status,
                "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
            })

        result = []
        for req in required_docs:
            doc_type = req["doc_type"]
            uploads = uploaded_map.get(doc_type, [])
            passed_uploads = [u for u in uploads if u["verification_status"]]
            result.append({
                "doc_type": doc_type,
                "label": req["label"],
                "uploaded_count": len(uploads),
                "passed_count": len(passed_uploads),
                "has_passed": len(passed_uploads) > 0,
                "uploads": uploads,
            })

        all_passed = all(item["has_passed"] for item in result) if result else False
        return Response({
            "project_id": str(project.id),
            "current_level": active_level,
            "required_docs": result,
            "all_required_passed": all_passed,
            "total_required": len(result),
            "completed_count": sum(1 for item in result if item["has_passed"]),
        })

    @action(detail=True, methods=["post"], url_path="chat")
    def chat(self, request, pk=None):
        """
        Stage 4: AI RAG & Chatbot Processing
        Ask questions against uploaded project documents.
        """
        project = self.get_object()
        question = request.data.get("question")

        if not question:
            return Response(
                {"detail": "Field 'question' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        documents = [
            {"doc_type": doc.doc_type, "text": doc.extracted_text}
            for doc in project.documents.all()
        ]

        answer = _gemini.ask_document_chat(
            question=question,
            documents=documents,
            project_context=project.objectives,
        )

        return Response({"project_id": str(project.id), "question": question, "answer": answer})

    @action(detail=True, methods=["post"], url_path="generate_deliverables")
    def generate_deliverables(self, request, pk=None):
        """
        Stage 5: Final Review & Deliverable Packaging
        Packages all documents:
          - Verified Documents (BRD, FRD, PRD, extracted texts)
          - Verification Summary
          - Project Timeline
          - Project Metadata
        """
        project = self.get_object()
        documents = project.documents.all()

        project_info = {
            "company_name": project.company_name,
            "project_name": project.project_name,
            "industry": project.industry,
            "objectives": project.objectives,
            "team_members": project.team_members,
            "expected_timeline": project.expected_timeline,
            "status": project.status,
            "readiness_score": project.readiness_score,
            "created_at": str(project.created_at),
        }

        # 1. Generated & Extracted Verified Documents
        doc_payloads = [
            {"doc_type": doc.doc_type, "text": doc.extracted_text}
            for doc in documents
        ]
        brd_content = _gemini.generate_deliverable("BRD", project_info, doc_payloads)
        frd_content = _gemini.generate_deliverable("FRD", project_info, doc_payloads)
        prd_content = _gemini.generate_deliverable("PRD", project_info, doc_payloads)

        files = {
            # Verified Documents folder
            f"Verified_Documents/BRD_{project.project_name}.md": brd_content,
            f"Verified_Documents/FRD_{project.project_name}.md": frd_content,
            f"Verified_Documents/PRD_{project.project_name}.md": prd_content,
        }

        # Add original/extracted text for uploaded docs
        for idx, doc in enumerate(documents, start=1):
            files[f"Verified_Documents/Uploaded_{doc.doc_type}_{idx}.txt"] = doc.extracted_text or "No extracted text"

        # 2. Verification Summary
        try:
            report = project.verification_report
            summary_content = (
                f"# Verification Summary\n\n"
                f"**Average Readiness Score**: {report.report_data.get('average_score', 0)}%\n\n"
                f"**Summary**: {report.summary}\n\n"
                f"## Document Verification Breakdown\n\n"
            )
            for doc_res in report.report_data.get("documents", []):
                summary_content += (
                    f"### Document ({doc_res.get('doc_type')})\n"
                    f"- **Passed**: {doc_res.get('passed')}\n"
                    f"- **Score**: {doc_res.get('score')}%\n"
                    f"- **Missing Keywords**: {', '.join(doc_res.get('missing_keywords', [])) or 'None'}\n"
                    f"- **Missing Sections**: {', '.join(doc_res.get('missing_sections', [])) or 'None'}\n"
                    f"- **AI Feedback**: {doc_res.get('ai_feedback') or 'N/A'}\n\n"
                )
        except Exception:
            summary_content = f"# Verification Summary\n\nReadiness Score: {project.readiness_score or 'N/A'}\nStatus: {project.status}"

        files["Verification_Summary.md"] = summary_content

        # 3. Project Timeline
        timeline_content = (
            f"# Project Timeline\n\n"
            f"**Project Name**: {project.project_name}\n"
            f"**Expected Timeline**: {project.expected_timeline or 'Not specified'}\n"
            f"**Created At**: {project.created_at}\n"
            f"**Current Status**: {project.status}\n"
        )
        files["Project_Timeline.md"] = timeline_content

        # 4. Project Metadata
        metadata_content = (
            f"# Project Metadata\n\n"
            f"- **ID**: {project.id}\n"
            f"- **Company Name**: {project.company_name}\n"
            f"- **Industry**: {project.industry}\n"
            f"- **Objectives**: {project.objectives}\n"
            f"- **Team Members**: {project.team_members}\n"
            f"- **Readiness Score**: {project.readiness_score}\n"
        )
        files["Project_Metadata.md"] = metadata_content

        zip_url = package_project_deliverables(str(project.id), files)

        project.status = "COMPLETED"
        project.save(update_fields=["status"])

        return Response(
            {
                "project_id": str(project.id),
                "status": project.status,
                "zip_download_url": zip_url,
                "contents": [
                    "Verified Documents/",
                    "Verification_Summary.md",
                    "Project_Timeline.md",
                    "Project_Metadata.md",
                ],
            }
        )


class DocumentUploadView(generics.CreateAPIView):
    """
    Stage 2: Document Upload & Parser
    Extracts text and performs fast rule verification.
    """
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        project_id = self.kwargs.get("pk")
        project = Project.objects.get(pk=project_id)
        file_obj = self.request.FILES["file"]
        # pyrefly: ignore [missing-attribute]
        doc_type = self.request.data.get("doc_type", "OTHER")
        active_level = _active_level(project)

        requested_level = self.request.data.get("level")
        if requested_level not in (None, ""):
            try:
                requested_level = int(requested_level)
            except (TypeError, ValueError):
                raise ValidationError({"level": "Level must be an integer."})
            if requested_level != active_level:
                raise ValidationError({"level": f"Documents can only be uploaded for the current unlocked level ({active_level})."})

        document = serializer.save(project=project, doc_type=doc_type, level=active_level, file=file_obj)

        extracted = extract_document_from_file(document.file.path)
        text = extracted.get("text", "")
        document.extracted_text = text

        verification = verify_level_document(document_text=text, level=active_level, document_data=extracted)
        document.verification_status = verification["passed"]
        document.missing_keywords = verification["missing_requirements"]
        document.missing_sections = verification["missing_requirements"]
        document.save()

        level_config = LEVEL_REQUIREMENTS.get(active_level, {})
        required_doc_types = [rd["doc_type"] for rd in level_config.get("required_documents", [])]

        all_required_passed = False
        if required_doc_types:
            docs_for_level = project.documents.filter(level=active_level)
            passed_doc_types = set(
                d.doc_type for d in docs_for_level if d.verification_status
            )
            all_required_passed = all(dt in passed_doc_types for dt in required_doc_types)
        else:
            all_required_passed = verification["passed"]

        if all_required_passed and active_level < TOTAL_LEVELS:
            project.completed_levels = sorted(set([*project.completed_levels, active_level]))
            project.current_level = min(active_level + 1, TOTAL_LEVELS)
            project.level_scores = [*project.level_scores, {"level": active_level, "score": verification["score"]}]
            project.status = "PROCESSING"
            project.readiness_score = verification["score"]
            project.save(update_fields=["completed_levels", "current_level", "level_scores", "status", "readiness_score"])
        elif all_required_passed and active_level >= TOTAL_LEVELS:
            project.completed_levels = sorted(set([*project.completed_levels, active_level]))
            project.level_scores = [*project.level_scores, {"level": active_level, "score": verification["score"]}]
            project.status = "COMPLETED"
            project.save(update_fields=["readiness_score", "status", "completed_levels", "level_scores"])
        else:
            project.readiness_score = verification["score"]
            project.status = "VERIFICATION"
            project.save(update_fields=["readiness_score", "status"])

        document_data = DocumentSerializer(document).data
        document_data["verification"] = verification
        document_data["extraction"] = extracted
        document_data["project_current_level"] = project.current_level
        document_data["all_required_passed"] = all_required_passed
        document_data["level_unlocked"] = all_required_passed
        return document_data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doc = self.perform_create(serializer)
        return Response(doc, status=status.HTTP_201_CREATED)

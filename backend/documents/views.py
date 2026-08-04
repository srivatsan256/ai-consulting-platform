import io
import zipfile
from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Document
from .serializers import DocumentSerializer
from .filters import DocumentFilter
from core.ai_service import (
    analyze_document,
    generate_verification_report,
    keyword_extraction,
    language_analysis,
    get_llm_client,
)
from core.rule_engine import validate_document
from core.document_processor import extract_text_from_uploaded_file
from core.vector_store import add_document as add_to_vector_store


class DocumentViewSet(viewsets.ModelViewSet):

    queryset = Document.objects.select_related(
        "project",
        "created_by",
        "updated_by"
    )

    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = DocumentFilter

    search_fields = [
        "title",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "version",
    ]

    ordering = ["-created_at"]

    @action(detail=False, methods=["post"])
    def extract_text(self, request):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response(
                {"error": "No file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            result = extract_text_from_uploaded_file(uploaded_file)
            return Response({
                "text": result["text"],
                "total_pages": result["total_pages"],
                "filename": uploaded_file.name,
            })
        except Exception as e:
            return Response(
                {"error": f"Extraction failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def analyze(self, request, pk=None):
        document = self.get_object()
        text = document.content
        if not text:
            return Response(
                {"error": "Document has no content to analyze."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            result = analyze_document(text)
            keywords = keyword_extraction(text)
            add_to_vector_store(
                doc_id=f"document_{document.pk}",
                text=text,
                metadata={
                    "type": "document",
                    "document_type": document.document_type,
                    "project_id": document.project_id,
                },
            )
            return Response({
                "analysis": result["analysis"],
                "keywords": keywords,
                "tokens_used": result.get("tokens_used", 0),
            })
        except Exception as e:
            return Response(
                {"error": f"Analysis failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def validate_document(self, request, pk=None):
        document = self.get_object()
        text = document.content
        if not text:
            return Response(
                {"error": "Document has no content to validate."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        custom_rules = request.data.get("rules", None)
        results = validate_document(text, custom_rules)
        return Response(results)

    @action(detail=True, methods=["post"])
    def language_check(self, request, pk=None):
        document = self.get_object()
        text = request.data.get("text", document.content)
        if not text:
            return Response(
                {"error": "No text to analyze."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            analysis = language_analysis(text)
            return Response(analysis)
        except Exception as e:
            return Response(
                {"error": f"Language analysis failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def verification_report(self, request, pk=None):
        document = self.get_object()
        text = document.content
        if not text:
            return Response(
                {"error": "Document has no content."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        rules = request.data.get("rules", [])
        try:
            result = generate_verification_report(text, rules)
            return Response({
                "report": result["report"],
                "tokens_used": result.get("tokens_used", 0),
            })
        except Exception as e:
            return Response(
                {"error": f"Verification failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def generate_document(self, request, pk=None):
        document = self.get_object()
        doc_type = request.data.get("document_type", document.document_type)
        project = document.project
        context = request.data.get("context", document.content)
        client = get_llm_client()
        try:
            type_names = dict(Document.DOCUMENT_TYPES)
            type_name = type_names.get(doc_type, doc_type)
            response = client.chat.completions.create(
                model="custom-model",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"You are an expert technical writer generating "
                            f"a {type_name} for a consulting project."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Generate a comprehensive {type_name} for project:\n"
                            f"Name: {project.project_name}\n"
                            f"Description: {project.description}\n"
                            f"Context:\n{context}\n\n"
                            f"Include all relevant sections and details."
                        ),
                    },
                ],
                temperature=0.4,
                max_tokens=4000,
            )
            generated_content = response.choices[0].message.content
            new_version = document.version + 1
            new_doc = Document.objects.create(
                project=project,
                document_type=doc_type,
                title=f"{document.title} - Generated v{new_version}",
                content=generated_content,
                version=new_version,
                status="draft",
                created_by=request.user,
                updated_by=request.user,
            )
            return Response({
                "message": "Document generated.",
                "document_id": new_doc.pk,
                "content": generated_content,
                "version": new_version,
            })
        except Exception as e:
            return Response(
                {"error": f"Generation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def download_project_zip(self, request):
        project_id = request.query_params.get("project_id")
        if not project_id:
            return Response(
                {"error": "project_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        documents = Document.objects.filter(
            project_id=project_id,
        ).select_related("project")
        if not documents.exists():
            return Response(
                {"error": "No documents found for this project."},
                status=status.HTTP_404_NOT_FOUND,
            )
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for doc in documents:
                filename = f"{doc.document_type}_{doc.title}_v{doc.version}.txt"
                zip_file.writestr(filename, doc.content or "No content")
            metadata_lines = []
            for doc in documents:
                metadata_lines.append(
                    f"{doc.document_type}: {doc.title} "
                    f"(v{doc.version}, {doc.status})"
                )
            zip_file.writestr(
                "PROJECT_METADATA.txt",
                f"Project: {documents.first().project.project_name}\n"
                f"Total Documents: {documents.count()}\n\n"
                f"Document Index:\n" + "\n".join(metadata_lines),
            )
        zip_buffer.seek(0)
        project_name = documents.first().project.project_name
        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = (
            f'attachment; filename="{project_name}_documents.zip"'
        )
        return response
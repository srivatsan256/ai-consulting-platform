from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiTypes, extend_schema

from .models import Project, ProjectPhase, Milestone, LevelModule, ProjectDocument
from .serializers import (
    ProjectSerializer,
    ProjectPhaseSerializer,
    MilestoneSerializer,
    LevelModuleSerializer,
    ProjectDocumentSerializer,
)
from .services.verification_service import (
    extract_text,
    verify_document,
    verify_project,
)
from .services.chat_service import answer_question
from .services.deliverables_service import generate_deliverables


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.select_related("company", "project_manager")
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "priority", "company", "project_manager"]
    search_fields = ["project_name", "description"]
    ordering_fields = ["project_name", "start_date", "created_at", "status"]
    ordering = ["-created_at"]


class ProjectPhaseViewSet(viewsets.ModelViewSet):
    queryset = ProjectPhase.objects.select_related("project")
    serializer_class = ProjectPhaseSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["project", "completed"]
    search_fields = ["phase_name"]
    ordering_fields = ["order", "created_at"]


class MilestoneViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.select_related("project")
    serializer_class = MilestoneSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["project", "completed"]
    search_fields = ["title"]
    ordering_fields = ["due_date", "created_at"]


def _tenant_company(request):
    tenant = getattr(request, "tenant", None)
    membership = getattr(tenant, "membership", None)
    if membership is None and getattr(request.user, "is_authenticated", False):
        from company_members.models import CompanyMember

        membership = CompanyMember.objects.primary_for_user(request.user) # type: ignore
    if membership is not None:
        return membership.company
    return None


def _tenant_scoped_project(request, pk):
    """Resolve a project restricted to the request user's company."""
    queryset = Project.objects.all()
    company = _tenant_company(request)
    if company:
        queryset = queryset.filter(company=company)
    return get_object_or_404(queryset, pk=pk)


class LevelModuleListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="level_modules_list",
        summary="List level modules",
        responses={200: LevelModuleSerializer(many=True)},
    )
    def get(self, request):
        modules = LevelModule.objects.all()
        return Response(
            LevelModuleSerializer(modules, many=True).data,
            status=status.HTTP_200_OK,
        )


class ProjectListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="projects_list",
        summary="List projects",
        responses={200: ProjectSerializer(many=True)},
    )
    def get(self, request):
        queryset = Project.objects.select_related("company")
        company = _tenant_company(request)
        if company:
            queryset = queryset.filter(company=company)
        queryset = queryset.order_by("-created_at")
        return Response(
            ProjectSerializer(
                queryset,
                many=True,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        operation_id="projects_create",
        summary="Create a project",
        request=ProjectSerializer,
        responses={201: ProjectSerializer},
    )
    def post(self, request):
        from core.enforcement import TenantEnforcement

        tenant = TenantEnforcement.require_tenant(request)
        TenantEnforcement.check_quota(
            tenant,
            "projects",
            Project.objects.filter(
                company=tenant.company,
                is_active=True,
            ).count(),
        )
        serializer = ProjectSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="projects_retrieve",
        summary="Retrieve a project",
        responses={200: ProjectSerializer},
    )
    def get(self, request, pk):
        project = _tenant_scoped_project(request, pk)
        return Response(
            ProjectSerializer(
                project,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        operation_id="projects_partial_update",
        summary="Partially update a project",
        request=ProjectSerializer,
        responses={200: ProjectSerializer},
    )
    def patch(self, request, pk):
        project = _tenant_scoped_project(request, pk)
        serializer = ProjectSerializer(
            project,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        operation_id="projects_update",
        summary="Update a project",
        request=ProjectSerializer,
        responses={200: ProjectSerializer},
    )
    def put(self, request, pk):
        return self.patch(request, pk)

    @extend_schema(
        operation_id="projects_destroy",
        summary="Delete a project",
        responses={204: None},
    )
    def delete(self, request, pk):
        project = _tenant_scoped_project(request, pk)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectDocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="projects_document_upload",
        summary="Upload a document for a project",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "format": "binary"},
                    "doc_type": {"type": "string"},
                    "level": {"type": "integer"},
                },
                "required": ["file"],
            }
        },
        responses={201: ProjectDocumentSerializer},
    )
    def post(self, request, pk):
        project = _tenant_scoped_project(request, pk)

        file = request.FILES.get("file")
        if not file:
            return Response(
                {"detail": "A file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        doc_type = (request.data.get("doc_type") or "OTHER").upper()
        try:
            level = int(request.data.get("level") or project.current_level or 1)
        except (TypeError, ValueError):
            level = max(1, project.current_level or 1)

        doc = ProjectDocument.objects.create(
            project=project,
            file=file,
            original_name=file.name,
            doc_type=doc_type,
            level=max(1, level),
            uploaded_by=request.user,
        )

        extract_text(doc)
        result = verify_document(doc)

        return Response(
            {
                "document": ProjectDocumentSerializer(
                    doc,
                    context={"request": request},
                ).data,
                "verification": {
                    "passed": result["passed"],
                    "score": result["score"],
                    "missing_requirements": result["missing_keywords"],
                },
            },
            status=status.HTTP_201_CREATED,
        )


class ProjectVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="projects_verify",
        summary="Verify a project",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "use_ai": {"type": "boolean"},
                },
            }
        },
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request, pk):
        project = _tenant_scoped_project(request, pk)
        use_ai = bool(request.data.get("use_ai", False))
        result = verify_project(project, use_ai=use_ai)
        return Response(result, status=status.HTTP_200_OK)


class ProjectChatView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="projects_chat",
        summary="Ask a question about a project",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                },
                "required": ["question"],
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "answer": {"type": "string"},
                },
            }
        },
    )
    def post(self, request, pk):
        project = _tenant_scoped_project(request, pk)
        question = request.data.get("question", "")
        return Response(
            {"answer": answer_question(project, question)},
            status=status.HTTP_200_OK,
        )


class ProjectDeliverablesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="projects_generate_deliverables",
        summary="Generate deliverables archive for a project",
        request=None,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "zip_download_url": {"type": "string"},
                },
            }
        },
    )
    def post(self, request, pk):
        project = _tenant_scoped_project(request, pk)
        url = generate_deliverables(project, request=request)
        return Response(
            {"zip_download_url": url},
            status=status.HTTP_200_OK,
        )


class RequiredDocStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id="projects_required_doc_status",
        summary="Get required document status for a project level",
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request, pk):
        project = _tenant_scoped_project(request, pk)
        level = max(1, project.current_level or 1)
        module = LevelModule.objects.filter(level=level).first()

        required_docs = []
        for item in (module.required_documents if module else []) or []:
            if isinstance(item, dict):
                doc_type = str(item.get("doc_type", "OTHER")).upper()
                label = item.get("label") or doc_type
            else:
                doc_type = str(item).upper()
                label = doc_type

            uploaded = project.uploaded_documents.filter( # type: ignore
                level=level,
                doc_type=doc_type,
            )
            required_docs.append(
                {
                    "doc_type": doc_type,
                    "label": label,
                    "has_passed": uploaded.filter(
                        verification_status=True
                    ).exists(),
                    "uploaded_count": uploaded.count(),
                }
            )

        return Response(
            {
                "current_level": level,
                "readiness_score": project.readiness_score,
                "required_docs": required_docs,
            },
            status=status.HTTP_200_OK,
        )

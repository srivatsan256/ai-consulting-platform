from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import AIAssessment, AIUseCase
from .serializers import AIAssessmentSerializer, AIUseCaseSerializer
from .filters import AIAssessmentFilter
from core.ai_service import get_llm_client
from core.enforcement import TenantEnforcement
from core.vector_store import add_document as add_to_vector_store
from core.prompt_manager import render_prompt, get_prompt
from projects.models import Project


class AIAssessmentViewSet(viewsets.ModelViewSet):

    serializer_class = AIAssessmentSerializer

    queryset = AIAssessment.objects.select_related(
        "project",
        "completed_by",
        "created_by",
    ).prefetch_related("use_cases")

    filterset_class = AIAssessmentFilter

    search_fields = [
        "project__project_name",
        "executive_summary",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "overall_score",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        tenant = getattr(self.request, "tenant", None)
        if tenant and tenant.company:
            return queryset.filter(project__company=tenant.company)
        return queryset.none()

    def _get_project_context(self, project):
        parts = [
            f"Project: {project.project_name}",
            f"Description: {project.description}",
            f"Objectives: {project.objectives}",
            f"Status: {project.status}",
            f"Priority: {project.priority}",
        ]
        try:
            discoveries = project.discoveries.all()
            for d in discoveries:
                try:
                    tc = d.text_content
                    parts.append(f"Discovery: {tc.business_problem}")
                    parts.append(f"Goals: {tc.business_goal}")
                except Exception:
                    pass
        except Exception:
            pass
        return "\n".join(parts)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        assessment = self.get_object()
        assessment.status = "completed"
        assessment.completed_by = request.user
        assessment.save()
        return Response({"message": "Assessment completed."})

    @action(detail=True, methods=["post"])
    def add_use_case(self, request, pk=None):
        assessment = self.get_object()
        serializer = AIUseCaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(assessment=assessment)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def ai_analyze(self, request, pk=None):
        TenantEnforcement.require_subscription(request)
        TenantEnforcement.require_feature(request, "custom_rag")
        assessment = self.get_object()
        project = assessment.project
        project_context = self._get_project_context(project)
        prompt = get_prompt("proposal_analysis")
        client = get_llm_client()
        try:
            response = client.chat.completions.create(
                model="custom-model",
                messages=[
                    {"role": "system", "content": prompt["system_prompt"]},
                    {"role": "user", "content": prompt["user_prompt"].replace("{input_text}", project_context)},
                ],
                temperature=prompt["temperature"],
                max_tokens=prompt["max_tokens"],
            )
            ai_response = response.choices[0].message.content
            import re
            score_match = re.search(r'(?:feasibility|score)[^\d]*(\d+)', ai_response, re.IGNORECASE)
            if score_match:
                score = int(score_match.group(1))
                score = min(max(score, 1), 5)
                assessment.overall_score = score
            assessment.executive_summary = ai_response
            assessment.status = "in_progress"
            assessment.save(update_fields=["overall_score", "executive_summary", "status"])
            add_to_vector_store(
                doc_id=f"assessment_{assessment.pk}",
                text=ai_response,
                metadata={
                    "type": "ai_assessment",
                    "project_id": project.pk,
                    "score": assessment.overall_score,
                },
            )
            TenantEnforcement.record_usage(request, "ai_requests_per_month")
            return Response({
                "message": "AI analysis completed.",
                "analysis": ai_response,
                "score": assessment.overall_score,
            })
        except Exception as e:
            return Response(
                {"error": f"AI analysis failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def ai_recommend(self, request, pk=None):
        TenantEnforcement.require_subscription(request)
        TenantEnforcement.require_feature(request, "custom_rag")
        assessment = self.get_object()
        project = assessment.project
        project_context = self._get_project_context(project)
        client = get_llm_client()
        try:
            response = client.chat.completions.create(
                model="custom-model",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI consulting expert. Based on the project "
                            "assessment, generate specific AI use case recommendations "
                            "with business value, feasibility, ROI, and timeline."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Based on this assessment:\n"
                            f"Score: {assessment.overall_score}\n"
                            f"Summary: {assessment.executive_summary}\n\n"
                            f"Project Context:\n{project_context}\n\n"
                            f"Recommend 3-5 AI use cases with:\n"
                            f"- Title\n"
                            f"- Description\n"
                            f"- Business Value\n"
                            f"- Priority (low/medium/high/critical)\n"
                            f"- Estimated ROI\n"
                            f"- Estimated Timeline"
                        ),
                    },
                ],
                temperature=0.4,
                max_tokens=2000,
            )
            ai_response = response.choices[0].message.content
            assessment.recommendations = ai_response
            assessment.save(update_fields=["recommendations"])
            TenantEnforcement.record_usage(request, "ai_requests_per_month")
            return Response({
                "message": "AI recommendations generated.",
                "recommendations": ai_response,
            })
        except Exception as e:
            return Response(
                {"error": f"AI recommendation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AIUseCaseViewSet(viewsets.ModelViewSet):

    serializer_class = AIUseCaseSerializer

    queryset = AIUseCase.objects.select_related("assessment")

    permission_classes = [IsAuthenticated]

    search_fields = [
        "title",
        "description",
    ]

    ordering_fields = [
        "created_at",
        "priority",
        "status",
    ]

    ordering = ["-created_at"]

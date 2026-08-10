from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .filters import ConversationFilter
from core.ai_service import generate_ai_response
from core.enforcement import TenantEnforcement
from core.vector_store import search_documents
from core.tenant_scoping import TenantScopedViewSetMixin


class ConversationViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = ConversationSerializer

    queryset = Conversation.objects.prefetch_related(
        "participants",
    )

    filterset_class = ConversationFilter

    search_fields = [
        "title",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
    ]

    ordering = ["-updated_at"]

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(
            participants=self.request.user,
        )

    @action(detail=True, methods=["get", "post"])
    def messages(self, request, pk=None):
        conversation = self.get_object()

        if request.method == "GET":
            messages = conversation.messages.select_related("sender")
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)

        serializer = MessageSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        msg = serializer.save(conversation=conversation)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def ai_chat(self, request):
        TenantEnforcement.check_ai_quota(request)
        message = request.data.get("message", "")
        conversation_id = request.data.get("conversation_id")
        project_id = request.data.get("project_id")
        if not message:
            return Response(
                {"error": "Message is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        kb_results = search_documents(message, n_results=3)
        kb_context = ""
        if kb_results:
            kb_context = "\n\n".join([
                r.get("document", "") for r in kb_results
            ])
        project_context = ""
        tenant = getattr(request, "tenant", None)
        if project_id and tenant is not None and tenant.company is not None:
            from projects.models import Project
            try:
                project = Project.objects.get(
                    pk=project_id,
                    company=tenant.company,
                )
                project_context = (
                    f"Project: {project.project_name}\n"
                    f"Description: {project.description}\n"
                    f"Status: {project.status}"
                )
            except Project.DoesNotExist:
                pass
        try:
            ai_reply = generate_ai_response(
                user_message=message,
                context=project_context,
                knowledge_base_context=kb_context,
            )
        except Exception as e:
            return Response(
                {"error": f"AI response failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        conversation = None
        if conversation_id:
            try:
                conversation = self.get_queryset().get(pk=conversation_id)
            except Conversation.DoesNotExist:
                pass
        if not conversation:
            conversation = Conversation.objects.create(
                title=f"AI Chat - {message[:50]}",
                conversation_type="direct",
                created_by=request.user,
            )
            conversation.participants.add(request.user)
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=message,
        )
        ai_user, _ = Message.objects.get_or_create(
            conversation=conversation,
        )
        Message.objects.create(
            conversation=conversation,
            content=ai_reply,
        )
        TenantEnforcement.record_usage(request, "ai_requests_per_month")
        return Response({
            "conversation_id": conversation.pk,
            "reply": ai_reply,
            "sources": [r.get("id", "") for r in kb_results],
        })


class MessageViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = MessageSerializer

    queryset = Message.objects.select_related("sender")

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(
            conversation__participants=self.request.user,
        )

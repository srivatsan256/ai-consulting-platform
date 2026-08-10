from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import KnowledgeBase, KBAttachment
from .serializers import KnowledgeBaseSerializer, KBAttachmentSerializer
from .filters import KnowledgeBaseFilter
from core.vector_store import (
    add_document as add_to_vector_store,
    search_documents,
    delete_document,
)
from core.tenant_scoping import TenantScopedViewSetMixin


class KnowledgeBaseViewSet(TenantScopedViewSetMixin, viewsets.ModelViewSet):

    serializer_class = KnowledgeBaseSerializer

    queryset = KnowledgeBase.objects.select_related(
        "project",
        "created_by",
        "updated_by",
    ).prefetch_related("attachments")

    filterset_class = KnowledgeBaseFilter

    search_fields = [
        "title",
        "content",
        "tags",
    ]

    ordering_fields = [
        "title",
        "view_count",
        "created_at",
        "updated_at",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        self._validate_tenant_scoped_fks(serializer.validated_data)
        kb = serializer.save(created_by=self.request.user)
        if kb.is_published and kb.content:
            metadata = {
                "type": "knowledge_base",
                "category": kb.category,
                "project_id": kb.project_id or 0,
            }
            if kb.tags:
                metadata["tags"] = kb.tags
            add_to_vector_store(
                doc_id=f"kb_{kb.pk}",
                text=f"{kb.title}\n\n{kb.content}",
                metadata=metadata,
            )

    def perform_update(self, serializer):
        self._validate_tenant_scoped_fks(serializer.validated_data)
        kb = serializer.save(updated_by=self.request.user)
        if kb.is_published and kb.content:
            metadata = {
                "type": "knowledge_base",
                "category": kb.category,
                "project_id": kb.project_id or 0,
            }
            if kb.tags:
                metadata["tags"] = kb.tags
            add_to_vector_store(
                doc_id=f"kb_{kb.pk}",
                text=f"{kb.title}\n\n{kb.content}",
                metadata=metadata,
            )

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        kb = self.get_object()
        kb.is_published = True
        kb.save(update_fields=["is_published"])
        if kb.content:
            metadata = {
                "type": "knowledge_base",
                "category": kb.category,
                "project_id": kb.project_id or 0,
            }
            if kb.tags:
                metadata["tags"] = kb.tags
            add_to_vector_store(
                doc_id=f"kb_{kb.pk}",
                text=f"{kb.title}\n\n{kb.content}",
                metadata=metadata,
            )
        return Response({"message": "Published."})

    @action(detail=True, methods=["post"])
    def unpublish(self, request, pk=None):
        kb = self.get_object()
        kb.is_published = False
        kb.save(update_fields=["is_published"])
        delete_document(f"kb_{kb.pk}")
        return Response({"message": "Unpublished."})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=["view_count"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def semantic_search(self, request):
        query = request.data.get("query", "")
        n_results = request.data.get("n_results", 5)
        if not query:
            return Response(
                {"error": "Query is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        results = search_documents(query, n_results=n_results)
        return Response({
            "query": query,
            "results": results,
            "count": len(results),
        })

    @action(detail=True, methods=["post"])
    def upload_attachment(self, request, pk=None):
        kb = self.get_object()
        uploaded = request.FILES.get("file")
        if not uploaded:
            return Response(
                {"error": "No file provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from file_management.services.storage import (
            enforce_plan_storage_quota,
            enforce_storage_quota,
        )

        enforce_storage_quota(kb.project.company, uploaded.size or 0)
        enforce_plan_storage_quota(kb.project.company, uploaded.size or 0)
        attachment = KBAttachment.objects.create(
            knowledge_base=kb,
            file=uploaded,
            original_filename=uploaded.name,
            file_size=uploaded.size,
        )
        serializer = KBAttachmentSerializer(attachment)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

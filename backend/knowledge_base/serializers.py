from rest_framework import serializers

from .models import KnowledgeBase, KBAttachment


class KBAttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = KBAttachment
        fields = [
            "id",
            "file",
            "original_filename",
            "file_size",
            "uploaded_at",
        ]
        read_only_fields = (
            "id",
            "original_filename",
            "file_size",
            "uploaded_at",
        )


class KnowledgeBaseSerializer(serializers.ModelSerializer):

    attachments = KBAttachmentSerializer(many=True, read_only=True)

    created_by_name = serializers.CharField(
        source="created_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = KnowledgeBase
        fields = [
            "id",
            "title",
            "content",
            "category",
            "project",
            "tags",
            "is_published",
            "view_count",
            "attachments",
            "created_by",
            "created_by_name",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "view_count",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["updated_by"] = self.context["request"].user
        return super().update(instance, validated_data)

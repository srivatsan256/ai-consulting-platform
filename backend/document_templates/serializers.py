from rest_framework import serializers

from .models import DocumentTemplate


class DocumentTemplateSerializer(serializers.ModelSerializer):

    created_by_name = serializers.CharField(
        source="created_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = DocumentTemplate
        fields = [
            "id",
            "name",
            "description",
            "category",
            "project",
            "file",
            "original_filename",
            "file_size",
            "version",
            "is_active",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "original_filename",
            "file_size",
            "created_by",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        uploaded = self.context["request"].FILES.get("file")
        if uploaded:
            validated_data["original_filename"] = uploaded.name
            validated_data["file_size"] = uploaded.size
        return super().create(validated_data)

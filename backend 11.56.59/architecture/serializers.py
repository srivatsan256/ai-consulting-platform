from rest_framework import serializers

from .models import ArchitectureDiagram, TechnologyStack


class ArchitectureDiagramSerializer(serializers.ModelSerializer):

    created_by_name = serializers.CharField(
        source="created_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = ArchitectureDiagram
        fields = [
            "id",
            "project",
            "title",
            "description",
            "category",
            "file",
            "diagram_url",
            "version",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "created_by",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class TechnologyStackSerializer(serializers.ModelSerializer):

    class Meta:
        model = TechnologyStack
        fields = [
            "id",
            "project",
            "name",
            "version",
            "category",
            "purpose",
            "license_type",
            "is_active",
            "created_at",
        ]
        read_only_fields = (
            "id",
            "created_at",
        )

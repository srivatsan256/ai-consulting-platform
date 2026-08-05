from rest_framework import serializers

from .models import Deployment


class DeploymentSerializer(serializers.ModelSerializer):

    deployed_by_name = serializers.CharField(
        source="deployed_by.get_full_name",
        read_only=True,
    )

    approved_by_name = serializers.CharField(
        source="approved_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = Deployment
        fields = [
            "id",
            "project",
            "title",
            "description",
            "version",
            "environment",
            "status",
            "deployed_by",
            "deployed_by_name",
            "approved_by",
            "approved_by_name",
            "changelog",
            "rollback_notes",
            "deployed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "deployed_by",
            "deployed_at",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        validated_data["deployed_by"] = self.context["request"].user
        return super().create(validated_data)

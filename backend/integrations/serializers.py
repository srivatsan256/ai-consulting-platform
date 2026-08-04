from rest_framework import serializers

from .models import Integration


class IntegrationSerializer(serializers.ModelSerializer):

    created_by_name = serializers.CharField(
        source="created_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = Integration
        fields = [
            "id",
            "project",
            "name",
            "integration_type",
            "status",
            "api_key",
            "api_url",
            "config",
            "last_sync_at",
            "error_message",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "last_sync_at",
            "error_message",
            "created_by",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)

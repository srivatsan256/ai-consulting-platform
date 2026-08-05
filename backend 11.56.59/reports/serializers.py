from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):

    created_by_name = serializers.CharField(
        source="created_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = Report
        fields = [
            "id",
            "project",
            "title",
            "report_type",
            "content",
            "status",
            "file",
            "created_by",
            "created_by_name",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "created_by",
            "published_at",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)

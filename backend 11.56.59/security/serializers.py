from rest_framework import serializers

from .models import SecurityChecklist, VulnerabilityReport


class SecurityChecklistSerializer(serializers.ModelSerializer):

    assigned_to_name = serializers.CharField(
        source="assigned_to.get_full_name",
        read_only=True,
    )

    verified_by_name = serializers.CharField(
        source="verified_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = SecurityChecklist
        fields = [
            "id",
            "project",
            "title",
            "description",
            "category",
            "status",
            "notes",
            "assigned_to",
            "assigned_to_name",
            "verified_by",
            "verified_by_name",
            "due_date",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "completed_at",
            "created_at",
            "updated_at",
        )


class VulnerabilityReportSerializer(serializers.ModelSerializer):

    reported_by_name = serializers.CharField(
        source="reported_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = VulnerabilityReport
        fields = [
            "id",
            "project",
            "title",
            "description",
            "severity",
            "status",
            "affected_component",
            "mitigation",
            "reported_by",
            "reported_by_name",
            "reported_date",
            "resolved_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "reported_by",
            "reported_date",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        validated_data["reported_by"] = self.context["request"].user
        return super().create(validated_data)

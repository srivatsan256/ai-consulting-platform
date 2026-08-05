from rest_framework import serializers

from .models import Risk


class RiskSerializer(serializers.ModelSerializer):

    owner_name = serializers.CharField(
        source="owner.get_full_name",
        read_only=True,
    )

    identified_by_name = serializers.CharField(
        source="identified_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = Risk
        fields = [
            "id",
            "project",
            "title",
            "description",
            "severity",
            "probability",
            "status",
            "mitigation_plan",
            "impact",
            "owner",
            "owner_name",
            "identified_by",
            "identified_by_name",
            "identified_date",
            "target_resolution_date",
            "resolved_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "identified_by",
            "identified_date",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        validated_data["identified_by"] = self.context["request"].user
        return super().create(validated_data)

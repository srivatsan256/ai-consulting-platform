from rest_framework import serializers

from .models import AIAssessment, AIUseCase


class AIUseCaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = AIUseCase
        fields = [
            "id",
            "assessment",
            "title",
            "description",
            "business_value",
            "technical_feasibility",
            "priority",
            "status",
            "estimated_roi",
            "estimated_timeline",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class AIAssessmentSerializer(serializers.ModelSerializer):

    use_cases = AIUseCaseSerializer(many=True, read_only=True)

    completed_by_name = serializers.CharField(
        source="completed_by.get_full_name",
        read_only=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = AIAssessment
        fields = [
            "id",
            "project",
            "status",
            "overall_score",
            "data_readiness_score",
            "infrastructure_score",
            "talent_score",
            "strategy_score",
            "executive_summary",
            "recommendations",
            "use_cases",
            "completed_by",
            "completed_by_name",
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

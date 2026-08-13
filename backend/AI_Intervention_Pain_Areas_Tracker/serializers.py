from rest_framework import serializers
from .models import AIInterventionPainArea


class NullableDateField(serializers.DateField):
    def to_internal_value(self, data):
        if data is None or data == "":
            return None
        return super().to_internal_value(data)


class AIInterventionPainAreaSerializer(serializers.ModelSerializer):
    target_date = NullableDateField(required=False, allow_null=True)

    class Meta: # type: ignore
        model = AIInterventionPainArea
        fields = [
            "id",
            "date",
            "department",
            "process_activity",
            "pain_area",
            "current_method",
            "frequency",
            "time_spent_hrs",
            "impact_area",
            "ai_intervention",
            "expected_benefit",
            "priority",
            "feasibility",
            "owner",
            "target_date",
            "status",
            "remarks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

from rest_framework import serializers
from .models import AIInterventionPainArea
from .scoring import (
    score_from_priority,
    score_from_time_spent,
    quadrant_from_scores,
)
from .recommendations import recommend


class NullableDateField(serializers.DateField):
    def to_internal_value(self, data):
        if data is None or data == "":
            return None
        return super().to_internal_value(data)


class AIInterventionPainAreaSerializer(serializers.ModelSerializer):
    target_date = NullableDateField(required=False, allow_null=True)
    impact_score = serializers.SerializerMethodField()
    feasibility_score = serializers.SerializerMethodField()
    priority_score = serializers.SerializerMethodField()
    total_score = serializers.SerializerMethodField()
    quadrant = serializers.SerializerMethodField()
    ai_recommendation = serializers.SerializerMethodField()
    ai_recommendation_key = serializers.SerializerMethodField()
    ai_recommendation_icon = serializers.SerializerMethodField()
    ai_confidence = serializers.SerializerMethodField()
    ai_reasoning = serializers.SerializerMethodField()

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
            "impact_score",
            "feasibility_score",
            "priority_score",
            "total_score",
            "quadrant",
            "ai_recommendation",
            "ai_recommendation_key",
            "ai_recommendation_icon",
            "ai_confidence",
            "ai_reasoning",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_impact_score(self, obj):
        return score_from_time_spent(obj.time_spent_hrs)

    def get_feasibility_score(self, obj):
        return score_from_priority(obj.feasibility)

    def get_priority_score(self, obj):
        return score_from_priority(obj.priority)

    def get_total_score(self, obj):
        return (
            self.get_impact_score(obj)
            + self.get_feasibility_score(obj)
            + self.get_priority_score(obj)
        )

    def get_quadrant(self, obj):
        return quadrant_from_scores(
            self.get_impact_score(obj),
            self.get_feasibility_score(obj),
        )

    def _recommendation(self, obj):
        if not hasattr(self, "_recommendation_cache"):
            self._recommendation_cache = {}
        if obj.id not in self._recommendation_cache:
            self._recommendation_cache[obj.id] = recommend(obj)
        return self._recommendation_cache[obj.id]

    def get_ai_recommendation(self, obj):
        return self._recommendation(obj)["name"]

    def get_ai_recommendation_key(self, obj):
        return self._recommendation(obj)["key"]

    def get_ai_recommendation_icon(self, obj):
        return self._recommendation(obj)["icon"]

    def get_ai_confidence(self, obj):
        return self._recommendation(obj)["confidence"]

    def get_ai_reasoning(self, obj):
        return self._recommendation(obj)["reasoning"]

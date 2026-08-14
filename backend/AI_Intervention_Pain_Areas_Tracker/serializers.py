from rest_framework import serializers
from .models import AIInterventionPainArea


class NullableDateField(serializers.DateField):
    def to_internal_value(self, data):
        if data is None or data == "":
            return None
        return super().to_internal_value(data)


# Mirrors the GENERATED ALWAYS AS expressions in
# sql/add_calculated_fields.sql (stored on the Supabase table).
def score_from_priority(value):
    return {"High": 3, "Medium": 2, "Low": 1}.get(value, 1)


def score_from_time_spent(time_spent_hrs):
    if time_spent_hrs is None:
        return 1
    if time_spent_hrs >= 40:
        return 3
    if time_spent_hrs >= 10:
        return 2
    return 1


def quadrant_from_scores(impact_score, feasibility_score):
    if impact_score >= 2 and feasibility_score >= 2:
        return "Quick Win"
    if impact_score >= 2:
        return "Strategic"
    if feasibility_score >= 2:
        return "Fill In"
    return "Revisit"


class AIInterventionPainAreaSerializer(serializers.ModelSerializer):
    target_date = NullableDateField(required=False, allow_null=True)
    impact_score = serializers.SerializerMethodField()
    feasibility_score = serializers.SerializerMethodField()
    priority_score = serializers.SerializerMethodField()
    quadrant = serializers.SerializerMethodField()

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
            "quadrant",
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

    def get_quadrant(self, obj):
        return quadrant_from_scores(
            self.get_impact_score(obj),
            self.get_feasibility_score(obj),
        )

from rest_framework import serializers

from .models import Approval


class ApprovalSerializer(serializers.ModelSerializer):

    requested_by_name = serializers.CharField(
        source="requested_by.get_full_name",
        read_only=True,
    )

    assigned_to_name = serializers.CharField(
        source="assigned_to.get_full_name",
        read_only=True,
    )

    class Meta:
        model = Approval
        fields = [
            "id",
            "project",
            "entity_type",
            "entity_id",
            "title",
            "description",
            "status",
            "requested_by",
            "requested_by_name",
            "assigned_to",
            "assigned_to_name",
            "decision_date",
            "remarks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "requested_by",
            "decision_date",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        validated_data["requested_by"] = self.context["request"].user
        return super().create(validated_data)

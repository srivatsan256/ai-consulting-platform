from rest_framework import serializers

from .models import Workflow, WorkflowStep, WorkflowExecution


class WorkflowStepSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkflowStep
        exclude = ("workflow",)


class WorkflowExecutionSerializer(serializers.ModelSerializer):

    initiated_by_name = serializers.CharField(
        source="initiated_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = WorkflowExecution
        fields = [
            "id",
            "workflow",
            "entity_type",
            "entity_id",
            "status",
            "current_step",
            "initiated_by",
            "initiated_by_name",
            "started_at",
            "completed_at",
        ]
        read_only_fields = (
            "id",
            "initiated_by",
            "started_at",
            "completed_at",
        )


class WorkflowSerializer(serializers.ModelSerializer):

    steps = WorkflowStepSerializer(many=True, read_only=True)

    created_by_name = serializers.CharField(
        source="created_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = Workflow
        fields = [
            "id",
            "project",
            "name",
            "description",
            "status",
            "trigger_event",
            "steps",
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

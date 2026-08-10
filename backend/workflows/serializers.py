from rest_framework import serializers

from .models import Workflow, WorkflowHistory, WorkflowStep, WorkflowExecution


class WorkflowStepSerializer(serializers.ModelSerializer):

    class Meta:
        model = WorkflowStep
        exclude = ("workflow",)


class WorkflowHistorySerializer(serializers.ModelSerializer):

    actor_name = serializers.SerializerMethodField()

    step_name = serializers.CharField(source="step.name", read_only=True)

    event_type_display = serializers.CharField(
        source="get_event_type_display",
        read_only=True,
    )

    class Meta:
        model = WorkflowHistory
        fields = [
            "id",
            "workflow",
            "workflow_execution",
            "step",
            "step_name",
            "actor",
            "actor_name",
            "event_type",
            "event_type_display",
            "message",
            "metadata",
            "created_at",
        ]
        read_only_fields = fields

    def get_actor_name(self, obj):
        if obj.actor_id:
            return obj.actor.get_full_name() or obj.actor.email
        return "System"


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

    project_name = serializers.CharField(
        source="project.project_name",
        read_only=True,
    )

    execution_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Workflow
        fields = [
            "id",
            "project",
            "project_name",
            "name",
            "description",
            "status",
            "trigger_event",
            "steps",
            "execution_count",
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

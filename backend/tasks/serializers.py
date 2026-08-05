from rest_framework import serializers

from .models import Task, TaskComment


class TaskCommentSerializer(serializers.ModelSerializer):

    author_name = serializers.CharField(
        source="author.get_full_name",
        read_only=True,
    )

    class Meta:
        model = TaskComment
        fields = [
            "id",
            "task",
            "author",
            "author_name",
            "content",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "author",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class TaskDetailSerializer(serializers.ModelSerializer):

    subtasks = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
    )

    assigned_to_name = serializers.CharField(
        source="assigned_to.get_full_name",
        read_only=True,
    )

    created_by_name = serializers.CharField(
        source="created_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "parent",
            "title",
            "description",
            "status",
            "priority",
            "assigned_to",
            "assigned_to_name",
            "estimated_hours",
            "actual_hours",
            "start_date",
            "due_date",
            "completed_at",
            "subtasks",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "completed_at",
            "created_by",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)

from rest_framework import serializers

from .models import Task, TaskComment, TaskAttachment


class TaskAttachmentSerializer(serializers.ModelSerializer):

    file_url = serializers.SerializerMethodField()

    uploaded_by_name = serializers.CharField(
        source="uploaded_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = TaskAttachment
        fields = [
            "id",
            "task",
            "file",
            "file_url",
            "original_name",
            "file_size",
            "content_type",
            "uploaded_by",
            "uploaded_by_name",
            "uploaded_at",
        ]
        read_only_fields = (
            "id",
            "task",
            "file_url",
            "original_name",
            "file_size",
            "content_type",
            "uploaded_by",
            "uploaded_at",
        )

    def get_file_url(self, obj) -> str | None:
        if not obj.file:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url


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
            "task",
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

    attachments = TaskAttachmentSerializer(many=True, read_only=True)

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
            "attachments",
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

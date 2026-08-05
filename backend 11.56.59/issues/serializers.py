from rest_framework import serializers

from .models import Issue, IssueComment


class IssueCommentSerializer(serializers.ModelSerializer):

    author_name = serializers.CharField(
        source="author.get_full_name",
        read_only=True,
    )

    class Meta:
        model = IssueComment
        fields = [
            "id",
            "issue",
            "author",
            "author_name",
            "content",
            "created_at",
        ]
        read_only_fields = (
            "id",
            "author",
            "created_at",
        )

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class IssueSerializer(serializers.ModelSerializer):

    assigned_to_name = serializers.CharField(
        source="assigned_to.get_full_name",
        read_only=True,
    )

    reported_by_name = serializers.CharField(
        source="reported_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = Issue
        fields = [
            "id",
            "project",
            "title",
            "description",
            "status",
            "priority",
            "category",
            "assigned_to",
            "assigned_to_name",
            "reported_by",
            "reported_by_name",
            "resolution_notes",
            "due_date",
            "resolved_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "reported_by",
            "resolved_date",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        validated_data["reported_by"] = self.context["request"].user
        return super().create(validated_data)

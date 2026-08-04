from rest_framework import serializers

from .models import Review, ReviewComment


class ReviewCommentSerializer(serializers.ModelSerializer):

    author_name = serializers.CharField(
        source="author.get_full_name",
        read_only=True,
    )

    class Meta:
        model = ReviewComment
        fields = [
            "id",
            "review",
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


class ReviewSerializer(serializers.ModelSerializer):

    reviewer_name = serializers.CharField(
        source="reviewer.get_full_name",
        read_only=True,
    )

    requested_by_name = serializers.CharField(
        source="requested_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "project",
            "title",
            "description",
            "review_type",
            "status",
            "reviewer",
            "reviewer_name",
            "requested_by",
            "requested_by_name",
            "rating",
            "feedback",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "requested_by",
            "completed_at",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        validated_data["requested_by"] = self.context["request"].user
        return super().create(validated_data)

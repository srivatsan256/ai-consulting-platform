from rest_framework import serializers

from .models import SystemSetting, UserProfile, Announcement


class SystemSettingSerializer(serializers.ModelSerializer):

    updated_by_name = serializers.CharField(
        source="updated_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = SystemSetting
        fields = [
            "id",
            "key",
            "value",
            "category",
            "description",
            "is_sensitive",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "updated_by",
            "created_at",
            "updated_at",
        )

    def update(self, instance, validated_data):
        validated_data["updated_by"] = self.context["request"].user
        return super().update(instance, validated_data)


class UserProfileSerializer(serializers.ModelSerializer):

    user_email = serializers.CharField(
        source="user.email",
        read_only=True,
    )

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "user_email",
            "avatar",
            "bio",
            "timezone",
            "language",
            "theme",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "user",
            "created_at",
            "updated_at",
        )


class AnnouncementSerializer(serializers.ModelSerializer):

    is_visible = serializers.BooleanField(read_only=True)

    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "message",
            "level",
            "scope",
            "company",
            "is_active",
            "scheduled_for",
            "expires_at",
            "created_by",
            "created_at",
            "updated_at",
            "is_visible",
        ]
        read_only_fields = (
            "id",
            "created_by",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        request = self.context.get("request")
        scope = attrs.get("scope", getattr(self.instance, "scope", None) or "tenant")
        if (
            scope == "global"
            and request
            and not getattr(request.user, "is_staff", False)
        ):
            raise serializers.ValidationError(
                {"scope": "Only staff users can create global announcements."}
            )
        return attrs

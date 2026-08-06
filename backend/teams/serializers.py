from rest_framework import serializers
from .models import Team, TeamMember


class TeamSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )

    member_count = serializers.IntegerField(
        source="members.count",
        read_only=True,
    )

    class Meta:
        model = Team
        fields = [
            "id",
            "department",
            "department_name",
            "team_name",
            "description",
            "is_active",
            "member_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")


class TeamMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source="user.get_full_name",
        read_only=True,
    )

    user_email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    class Meta:
        model = TeamMember
        fields = [
            "id",
            "team",
            "user",
            "user_name",
            "user_email",
            "role",
            "created_at",
        ]
        read_only_fields = ("id", "created_at")

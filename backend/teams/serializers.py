from rest_framework import serializers
from .models import Team


class TeamSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="department.name",
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
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")

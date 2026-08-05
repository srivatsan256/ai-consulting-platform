from rest_framework import serializers

from .models import DashboardWidget


class DashboardWidgetSerializer(serializers.ModelSerializer):

    class Meta:
        model = DashboardWidget
        fields = [
            "id",
            "title",
            "widget_type",
            "config",
            "position",
            "is_visible",
            "owner",
            "project",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "owner",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)

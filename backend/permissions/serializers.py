from rest_framework import serializers
from .models import Permission


class PermissionSerializer(serializers.ModelSerializer):

    role_name = serializers.CharField(
        source="role.display_name",
        read_only=True
    )

    class Meta:
        model = Permission
        fields = "__all__"
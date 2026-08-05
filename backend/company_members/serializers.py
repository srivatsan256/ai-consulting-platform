from rest_framework import serializers
from .models import CompanyMember


class CompanyMemberSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.company_name", read_only=True)
    role_name = serializers.CharField(source="role.display_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = CompanyMember
        fields = [
            "id",
            "user",
            "user_email",
            "company",
            "company_name",
            "role",
            "role_name",
            "is_primary",
            "is_active",
            "joined_at",
            "last_accessed_at",
        ]
        read_only_fields = ["joined_at", "last_accessed_at"]


class SwitchCompanySerializer(serializers.Serializer):
    company_id = serializers.IntegerField(help_text="Company ID to switch to")

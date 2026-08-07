from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from departments.models import Department
from roles.models import Role
from .models import CompanyMember, UserInvitation


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


class InviteUserSerializer(serializers.Serializer):
    """Payload for inviting a user to join the acting company."""

    email = serializers.EmailField()
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=False,
        allow_null=True,
    )


class UserInvitationSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.display_name", read_only=True)
    company_name = serializers.CharField(
        source="company.company_name",
        read_only=True,
    )

    class Meta:
        model = UserInvitation
        fields = [
            "id",
            "company",
            "company_name",
            "email",
            "role",
            "role_name",
            "department",
            "invited_by",
            "token",
            "status",
            "expires_at",
            "accepted_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "company",
            "company_name",
            "email",
            "invited_by",
            "token",
            "status",
            "expires_at",
            "accepted_at",
            "created_at",
        ]


class AcceptInvitationSerializer(serializers.Serializer):
    """Payload for accepting an invitation."""

    token = serializers.CharField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": ["Passwords do not match."]}
            )
        validate_password(attrs["password"])
        return attrs

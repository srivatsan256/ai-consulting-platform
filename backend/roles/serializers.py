from rest_framework import serializers
from .models import Role, RoleAssignment


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class AssignRoleSerializer(serializers.Serializer):
    user = serializers.IntegerField(help_text="ID of the target user.")
    role = serializers.IntegerField(help_text="ID of the role to assign.")
    company = serializers.IntegerField(
        required=False,
        help_text="Company to assign in. Defaults to the acting user's tenant company.",
    )


class RoleAssignmentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    company_id = serializers.IntegerField(source="company.id", read_only=True)
    company_name = serializers.CharField(
        source="company.company_name",
        read_only=True,
    )
    role_id = serializers.IntegerField(source="role.id", read_only=True)
    role_key = serializers.CharField(source="role.role_key", read_only=True)
    role_name = serializers.CharField(source="role.display_name", read_only=True)
    previous_role_id = serializers.IntegerField(
        source="previous_role.id",
        read_only=True,
    )
    previous_role_key = serializers.CharField(
        source="previous_role.role_key",
        read_only=True,
    )
    assigned_by_email = serializers.EmailField(
        source="assigned_by.email",
        read_only=True,
    )

    class Meta:
        model = RoleAssignment
        fields = [
            "id",
            "user",
            "user_id",
            "user_email",
            "company",
            "company_id",
            "company_name",
            "role",
            "role_id",
            "role_key",
            "role_name",
            "previous_role",
            "previous_role_id",
            "previous_role_key",
            "assigned_by",
            "assigned_by_email",
            "created_at",
        ]
        read_only_fields = fields


class RolePermissionOutputSerializer(serializers.Serializer):
    """A single feature row of a role's permission matrix."""

    feature = serializers.CharField()
    can_view = serializers.BooleanField()
    can_create = serializers.BooleanField()
    can_update = serializers.BooleanField()
    can_delete = serializers.BooleanField()
    can_review = serializers.BooleanField()
    can_approve = serializers.BooleanField()
    can_export = serializers.BooleanField()


class MyRoleSerializer(serializers.Serializer):
    """The acting user's role plus the granted feature permissions."""

    id = serializers.IntegerField()
    role_key = serializers.CharField()
    display_name = serializers.CharField()
    permissions = RolePermissionOutputSerializer(many=True, required=False)

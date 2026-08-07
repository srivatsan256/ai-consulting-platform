from typing import Optional

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import Department, DepartmentMember


class DepartmentDetailSerializer(serializers.ModelSerializer):

    company_name = serializers.CharField(
        source="company.name",
        read_only=True,
    )

    head_name = serializers.SerializerMethodField()

    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Department

        fields = [
            "id",
            "company",
            "company_name",
            "name",
            "code",
            "description",
            "head",
            "head_name",
            "email",
            "phone",
            "location",
            "status",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]

        read_only_fields = (
            "id",
            "created_by",
            "created_at",
            "updated_at",
        )

    @extend_schema_field(field=serializers.CharField(required=False))
    def get_head_name(self, obj) -> Optional[str]:
        if obj.head:
            return obj.head.get_full_name() or obj.head.username
        return None

    @extend_schema_field(field=serializers.CharField(required=False))
    def get_created_by_name(self, obj) -> Optional[str]:
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None

    def validate_name(self, value):
        return value.strip()

    def validate_code(self, value):
        return value.strip().upper()

    def validate(self, attrs):

        company = attrs.get(
            "company",
            self.instance.company if self.instance else None,
        )

        name = attrs.get(
            "name",
            self.instance.name if self.instance else None,
        )

        code = attrs.get(
            "code",
            self.instance.code if self.instance else None,
        )

        queryset = Department.objects.filter(company=company)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.filter(name__iexact=name).exists():
            raise serializers.ValidationError(
                {"name": "Department name already exists."}
            )

        if queryset.filter(code__iexact=code).exists():
            raise serializers.ValidationError(
                {"code": "Department code already exists."}
            )

        return attrs

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class DepartmentMemberSerializer(serializers.ModelSerializer):

    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.SerializerMethodField()
    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )
    department_code = serializers.CharField(
        source="department.code",
        read_only=True,
    )
    company_id = serializers.IntegerField(
        source="department.company_id",
        read_only=True,
    )
    is_head = serializers.SerializerMethodField()

    class Meta:
        model = DepartmentMember
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "department",
            "department_name",
            "department_code",
            "company_id",
            "is_head",
            "is_active",
            "joined_at",
        ]
        read_only_fields = ["joined_at"]

    @extend_schema_field(field=serializers.CharField(required=False))
    def get_user_name(self, obj) -> Optional[str]:
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return None

    @extend_schema_field(field=serializers.BooleanField())
    def get_is_head(self, obj) -> bool:
        return obj.department.head_id == obj.user_id

    def validate(self, attrs):
        request = self.context.get("request")
        tenant = getattr(request, "tenant", None)

        department = attrs.get(
            "department",
            self.instance.department if self.instance else None,
        )

        if department is None:
            raise serializers.ValidationError(
                {"department": "Department is required."}
            )

        if tenant is None or tenant.company is None:
            raise serializers.ValidationError(
                "An active company membership is required."
            )

        if department.company_id != tenant.company.id:
            raise serializers.ValidationError(
                {"department": "Department must belong to your company."}
            )

        user = attrs.get("user", self.instance.user if self.instance else None)

        if user is not None:
            from company_members.models import CompanyMember

            if not CompanyMember.objects.filter(
                user=user,
                company=tenant.company,
                is_active=True,
            ).exists():
                raise serializers.ValidationError(
                    {"user": "User is not an active member of this company."}
                )

        return attrs
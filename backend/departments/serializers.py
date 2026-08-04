from typing import Optional

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import Department


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
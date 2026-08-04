from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    """
    Base serializer with common fields and validation.
    """

    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        abstract = True
        fields = [
            "id",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


class CompanyBaseModelSerializer(BaseModelSerializer):
    """
    Base serializer for tenant-aware models.
    """

    company = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta(BaseModelSerializer.Meta):
        fields = BaseModelSerializer.Meta.fields + ["company"]


class ReadSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for related objects.
    """

    class Meta:
        abstract = True
        fields = ["id", "name"]

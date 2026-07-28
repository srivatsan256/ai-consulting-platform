from rest_framework import serializers
from .models import (
    LevelModule, LevelMustInclude, LevelRecommended,
    LevelKeyPrompt, LevelRequiredDoc, LevelRequirementItem,
)


class LevelMustIncludeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelMustInclude
        fields = ["id", "text", "order"]
        read_only_fields = ["id"]


class LevelRecommendedSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelRecommended
        fields = ["id", "text", "order"]
        read_only_fields = ["id"]


class LevelKeyPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelKeyPrompt
        fields = ["id", "text", "order"]
        read_only_fields = ["id"]


class LevelRequiredDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelRequiredDoc
        fields = ["id", "doc_type", "label", "order"]
        read_only_fields = ["id"]


class LevelRequirementItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelRequirementItem
        fields = ["id", "key", "label", "is_required", "aliases", "order"]
        read_only_fields = ["id"]


class LevelModuleSerializer(serializers.ModelSerializer):
    must_include = LevelMustIncludeSerializer(source="must_include_items", many=True, read_only=True)
    recommended = LevelRecommendedSerializer(source="recommended_items", many=True, read_only=True)
    key_prompts = LevelKeyPromptSerializer(source="key_prompts_items", many=True, read_only=True)
    required_documents = LevelRequiredDocSerializer(source="required_doc_items", many=True, read_only=True)
    requirements = LevelRequirementItemSerializer(source="requirement_items", many=True, read_only=True)

    required_count = serializers.SerializerMethodField()
    recommended_count = serializers.SerializerMethodField()

    class Meta:
        model = LevelModule
        fields = [
            "id", "level", "title", "icon", "color", "description",
            "is_active", "order",
            "must_include", "recommended", "key_prompts",
            "required_documents", "requirements",
            "required_count", "recommended_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_required_count(self, obj):
        return obj.requirement_items.filter(is_required=True).count()

    def get_recommended_count(self, obj):
        return obj.requirement_items.filter(is_required=False).count()


class LevelModuleWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating level modules with nested items."""

    must_include = LevelMustIncludeSerializer(many=True, required=False)
    recommended = LevelRecommendedSerializer(many=True, required=False)
    key_prompts = LevelKeyPromptSerializer(many=True, required=False)
    required_documents = LevelRequiredDocSerializer(many=True, required=False)
    requirements = LevelRequirementItemSerializer(many=True, required=False)

    class Meta:
        model = LevelModule
        fields = [
            "id", "level", "title", "icon", "color", "description",
            "is_active", "order",
            "must_include", "recommended", "key_prompts",
            "required_documents", "requirements",
        ]

    def create(self, validated_data):
        must_include_data = validated_data.pop("must_include", [])
        recommended_data = validated_data.pop("recommended", [])
        key_prompts_data = validated_data.pop("key_prompts", [])
        required_docs_data = validated_data.pop("required_documents", [])
        requirements_data = validated_data.pop("requirements", [])

        module = LevelModule.objects.create(**validated_data)

        for item in must_include_data:
            LevelMustInclude.objects.create(module=module, **item)
        for item in recommended_data:
            LevelRecommended.objects.create(module=module, **item)
        for item in key_prompts_data:
            LevelKeyPrompt.objects.create(module=module, **item)
        for item in required_docs_data:
            LevelRequiredDoc.objects.create(module=module, **item)
        for item in requirements_data:
            LevelRequirementItem.objects.create(module=module, **item)

        return module

    def update(self, instance, validated_data):
        must_include_data = validated_data.pop("must_include", None)
        recommended_data = validated_data.pop("recommended", None)
        key_prompts_data = validated_data.pop("key_prompts", None)
        required_docs_data = validated_data.pop("required_documents", None)
        requirements_data = validated_data.pop("requirements", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if must_include_data is not None:
            instance.must_include_items.all().delete()
            for item in must_include_data:
                LevelMustInclude.objects.create(module=instance, **item)
        if recommended_data is not None:
            instance.recommended_items.all().delete()
            for item in recommended_data:
                LevelRecommended.objects.create(module=instance, **item)
        if key_prompts_data is not None:
            instance.key_prompts_items.all().delete()
            for item in key_prompts_data:
                LevelKeyPrompt.objects.create(module=instance, **item)
        if required_docs_data is not None:
            instance.required_doc_items.all().delete()
            for item in required_docs_data:
                LevelRequiredDoc.objects.create(module=instance, **item)
        if requirements_data is not None:
            instance.requirement_items.all().delete()
            for item in requirements_data:
                LevelRequirementItem.objects.create(module=instance, **item)

        return instance

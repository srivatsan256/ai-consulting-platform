from rest_framework import serializers

from .models import (
    Discovery,
    DiscoveryText,
    DiscoveryDocument,
)


class DiscoveryTextSerializer(serializers.ModelSerializer):

    class Meta:
        model = DiscoveryText
        exclude = ("discovery",)


class DiscoveryDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = DiscoveryDocument
        exclude = ("discovery",)


class DiscoverySerializer(serializers.ModelSerializer):

    text_content = DiscoveryTextSerializer(required=False)

    document = DiscoveryDocumentSerializer(required=False)

    class Meta:
        model = Discovery

        fields = "__all__"

    def validate(self, attrs):

        input_type = attrs.get("input_type")

        text = self.initial_data.get("text_content")

        document = self.initial_data.get("document")

        if input_type == "text" and not text:
            raise serializers.ValidationError(
                {
                    "text_content":
                    "Text content is required."
                }
            )

        if input_type == "pdf" and not document:
            raise serializers.ValidationError(
                {
                    "document":
                    "Document is required."
                }
            )

        return attrs

    def create(self, validated_data):

        text_data = validated_data.pop(
            "text_content",
            None
        )

        document_data = validated_data.pop(
            "document",
            None
        )

        discovery = Discovery.objects.create(
            **validated_data
        )

        if discovery.input_type == "text":

            DiscoveryText.objects.create(
                discovery=discovery,
                **text_data
            )

        elif discovery.input_type == "pdf":

            DiscoveryDocument.objects.create(
                discovery=discovery,
                **document_data
            )

        return discovery

    def update(self, instance, validated_data):

        text_data = validated_data.pop(
            "text_content",
            None
        )

        document_data = validated_data.pop(
            "document",
            None
        )

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        if text_data:

            DiscoveryText.objects.update_or_create(
                discovery=instance,
                defaults=text_data,
            )

        if document_data:

            DiscoveryDocument.objects.update_or_create(
                discovery=instance,
                defaults=document_data,
            )

        return instance
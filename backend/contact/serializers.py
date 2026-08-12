from rest_framework import serializers

from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactMessage
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "inquiry_type",
            "message",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]

    def validate_message(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Message is required.")
        if len(value) > 5000:
            raise serializers.ValidationError("Message must be 5000 characters or fewer.")
        return value.strip()

    def validate_first_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("First name is required.")
        return value.strip()

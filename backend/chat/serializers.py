from typing import Optional

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):

    sender_email = serializers.CharField(
        source="sender.email",
        read_only=True,
    )

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "sender_email",
            "content",
            "attachment",
            "is_edited",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "sender",
            "is_edited",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        validated_data["sender"] = self.context["request"].user
        return super().create(validated_data)


class ConversationSerializer(serializers.ModelSerializer):

    last_message = serializers.SerializerMethodField()

    participant_count = serializers.IntegerField(
        source="participants.count",
        read_only=True,
    )

    class Meta:
        model = Conversation
        fields = [
            "id",
            "title",
            "conversation_type",
            "project",
            "participants",
            "created_by",
            "last_message",
            "participant_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "created_by",
            "created_at",
            "updated_at",
        )

    @extend_schema_field(field=MessageSerializer(required=False))
    def get_last_message(self, obj) -> Optional[dict]:
        last = obj.messages.order_by("-created_at").first()
        if last:
            return MessageSerializer(last).data
        return None

    def create(self, validated_data):
        participants = validated_data.pop("participants", [])
        validated_data["created_by"] = self.context["request"].user
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.set(participants)
        return conversation

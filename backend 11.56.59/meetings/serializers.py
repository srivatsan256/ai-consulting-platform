from rest_framework import serializers

from .models import Meeting, MeetingMinutes


class MeetingMinutesSerializer(serializers.ModelSerializer):

    created_by_name = serializers.CharField(
        source="created_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = MeetingMinutes
        fields = [
            "id",
            "meeting",
            "summary",
            "action_items",
            "decisions",
            "notes",
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

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class MeetingSerializer(serializers.ModelSerializer):

    minutes = MeetingMinutesSerializer(read_only=True)

    organizer_name = serializers.CharField(
        source="organizer.get_full_name",
        read_only=True,
    )

    participant_count = serializers.IntegerField(
        source="participants.count",
        read_only=True,
    )

    class Meta:
        model = Meeting
        fields = [
            "id",
            "title",
            "description",
            "project",
            "meeting_url",
            "location",
            "status",
            "start_time",
            "end_time",
            "organizer",
            "organizer_name",
            "participants",
            "participant_count",
            "minutes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "organizer",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        participants = validated_data.pop("participants", [])
        validated_data["organizer"] = self.context["request"].user
        meeting = Meeting.objects.create(**validated_data)
        meeting.participants.set(participants)
        return meeting

from django.contrib import admin

from .models import Meeting, MeetingMinutes


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "project",
        "status",
        "organizer",
        "start_time",
        "end_time",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "title",
        "description",
    )


@admin.register(MeetingMinutes)
class MeetingMinutesAdmin(admin.ModelAdmin):

    list_display = (
        "meeting",
        "created_by",
        "created_at",
    )

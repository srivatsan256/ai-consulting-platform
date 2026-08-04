from django.db import models

from accounts.models import User
from projects.models import Project


class Meeting(models.Model):

    STATUS = [
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="meetings",
    )

    meeting_url = models.URLField(blank=True)

    location = models.CharField(max_length=255, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="scheduled",
    )

    start_time = models.DateTimeField()

    end_time = models.DateTimeField(
        null=True,
        blank=True,
    )

    organizer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="meetings_organized",
    )

    participants = models.ManyToManyField(
        User,
        related_name="meetings",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "meetings"
        ordering = ["-start_time"]

    def __str__(self):
        return self.title


class MeetingMinutes(models.Model):

    meeting = models.OneToOneField(
        Meeting,
        on_delete=models.CASCADE,
        related_name="minutes",
    )

    summary = models.TextField()

    action_items = models.TextField(blank=True)

    decisions = models.TextField(blank=True)

    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="meeting_minutes_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "meeting_minutes"

    def __str__(self):
        return f"Minutes for {self.meeting.title}"

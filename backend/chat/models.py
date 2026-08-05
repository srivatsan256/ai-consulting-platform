from django.db import models

from accounts.models import User
from projects.models import Project


class Conversation(models.Model):

    CONVERSATION_TYPE = [
        ("direct", "Direct"),
        ("group", "Group"),
        ("project", "Project"),
    ]

    title = models.CharField(max_length=255, blank=True)

    conversation_type = models.CharField(
        max_length=20,
        choices=CONVERSATION_TYPE,
        default="direct",
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="conversations",
    )

    participants = models.ManyToManyField(
        User,
        related_name="conversations",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="conversations_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conversations"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title or f"Conversation {self.pk}"


class Message(models.Model):

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sent_messages",
    )

    content = models.TextField()

    attachment = models.FileField(
        upload_to="chat_attachments/",
        blank=True,
        null=True,
    )

    is_edited = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "messages"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender} - {self.content[:50]}"

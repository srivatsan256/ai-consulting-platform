from django.db import models

from accounts.models import User
from projects.models import Project


class KnowledgeBase(models.Model):

    CATEGORY = [
        ("article", "Article"),
        ("faq", "FAQ"),
        ("guide", "Guide"),
        ("template", "Template"),
        ("best_practice", "Best Practice"),
        ("lesson_learned", "Lesson Learned"),
    ]

    title = models.CharField(max_length=255)

    content = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=CATEGORY,
        default="article",
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="knowledge_base_entries",
    )

    tags = models.CharField(
        max_length=500,
        blank=True,
    )

    is_published = models.BooleanField(default=False)

    view_count = models.PositiveIntegerField(default=0)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="kb_entries_created",
    )

    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="kb_entries_updated",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "knowledge_base"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class KBAttachment(models.Model):

    knowledge_base = models.ForeignKey(
        KnowledgeBase,
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    file = models.FileField(
        upload_to="kb_attachments/",
    )

    original_filename = models.CharField(max_length=255)

    file_size = models.BigIntegerField(default=0)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "kb_attachments"

    def __str__(self):
        return self.original_filename

import uuid
from django.db import models


class LevelModule(models.Model):
    """Stores level module definitions in the database.
    Each level has a title, description, must_include items, recommended items, and key prompts.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    level = models.IntegerField(unique=True, help_text="Level number 1-11")
    title = models.CharField(max_length=200)
    icon = models.CharField(max_length=50, default="folder")
    color = models.CharField(max_length=30, default="gray")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["level"]

    def __str__(self):
        return f"Level {self.level}: {self.title}"


class LevelMustInclude(models.Model):
    """Required items for a level module."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(LevelModule, on_delete=models.CASCADE, related_name="must_include_items")
    text = models.CharField(max_length=500)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Must Include: {self.text[:60]}"


class LevelRecommended(models.Model):
    """Recommended items for a level module."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(LevelModule, on_delete=models.CASCADE, related_name="recommended_items")
    text = models.CharField(max_length=500)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Recommended: {self.text[:60]}"


class LevelKeyPrompt(models.Model):
    """AI prompts for a level module."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(LevelModule, on_delete=models.CASCADE, related_name="key_prompts_items")
    text = models.CharField(max_length=500)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Prompt: {self.text[:60]}"


class LevelRequiredDoc(models.Model):
    """Required documents for a level module."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(LevelModule, on_delete=models.CASCADE, related_name="required_doc_items")
    doc_type = models.CharField(max_length=50)
    label = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Doc: {self.label}"


class LevelRequirementItem(models.Model):
    """Individual requirements within a level, marked as required or recommended."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(LevelModule, on_delete=models.CASCADE, related_name="requirement_items")
    key = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    is_required = models.BooleanField(default=True)
    aliases = models.JSONField(default=list, blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{'Required' if self.is_required else 'Recommended'}: {self.label}"

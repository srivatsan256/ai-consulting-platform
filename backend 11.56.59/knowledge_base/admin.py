from django.contrib import admin

from .models import KnowledgeBase, KBAttachment


class KBAttachmentInline(admin.TabularInline):
    model = KBAttachment
    extra = 0
    readonly_fields = ("original_filename", "file_size", "uploaded_at")


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "category",
        "project",
        "is_published",
        "view_count",
        "created_by",
        "created_at",
    )

    list_filter = (
        "category",
        "is_published",
    )

    search_fields = (
        "title",
        "content",
        "tags",
    )

    inlines = [KBAttachmentInline]


@admin.register(KBAttachment)
class KBAttachmentAdmin(admin.ModelAdmin):

    list_display = (
        "knowledge_base",
        "original_filename",
        "file_size",
        "uploaded_at",
    )

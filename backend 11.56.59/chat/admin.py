from django.contrib import admin

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("sender", "content", "created_at")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "conversation_type",
        "project",
        "created_by",
        "created_at",
    )

    list_filter = (
        "conversation_type",
    )

    search_fields = (
        "title",
    )

    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    list_display = (
        "conversation",
        "sender",
        "content",
        "created_at",
    )

    search_fields = (
        "content",
    )

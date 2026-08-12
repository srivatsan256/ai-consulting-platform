from django.contrib import admin
from django.utils import timezone

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):

    list_display = (
        "first_name",
        "last_name",
        "email",
        "inquiry_type",
        "is_handled",
        "created_at",
    )

    list_filter = (
        "inquiry_type",
        "is_handled",
    )

    search_fields = (
        "first_name",
        "last_name",
        "email",
        "message",
    )

    actions = ["mark_as_handled"]

    @admin.action(description="Mark selected messages as handled")
    def mark_as_handled(self, request, queryset):
        queryset.update(is_handled=True, handled_at=timezone.now())

from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "action",
        "entity_type",
        "entity_name",
        "ip_address",
        "timestamp",
    )

    list_filter = (
        "action",
        "entity_type",
    )

    search_fields = (
        "user__email",
        "entity_name",
    )

    readonly_fields = (
        "user",
        "action",
        "entity_type",
        "entity_id",
        "entity_name",
        "changes",
        "ip_address",
        "user_agent",
        "timestamp",
    )

from django.contrib import admin
from .models import Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "role_key",
        "is_active",
    )

    list_filter = ("is_active",)

    search_fields = (
        "display_name",
        "role_key",
    )

    ordering = ("display_name",)
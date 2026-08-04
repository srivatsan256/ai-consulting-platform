from django.contrib import admin
from .models import Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "team_name",
        "department",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "department",
    )

    search_fields = (
        "team_name",
        "department__name",
    )

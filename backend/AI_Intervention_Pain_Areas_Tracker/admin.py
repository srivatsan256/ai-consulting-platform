from django.contrib import admin
from .models import AIInterventionPainArea


@admin.register(AIInterventionPainArea)
class AIInterventionPainAreaAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "department",
        "process_activity",
        "priority",
        "feasibility",
        "status",
        "owner",
        "target_date",
        "created_at",
    )
    list_filter = ("status", "priority", "feasibility", "department", "date")
    search_fields = (
        "process_activity",
        "pain_area",
        "ai_intervention",
        "owner",
        "department",
        "remarks",
    )
    readonly_fields = ("created_at", "updated_at")

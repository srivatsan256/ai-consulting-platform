from django.contrib import admin

from .models import AIAssessment, AIUseCase


class AIUseCaseInline(admin.TabularInline):
    model = AIUseCase
    extra = 0


@admin.register(AIAssessment)
class AIAssessmentAdmin(admin.ModelAdmin):

    list_display = (
        "project",
        "status",
        "overall_score",
        "completed_by",
        "created_at",
    )

    list_filter = (
        "status",
        "overall_score",
    )

    search_fields = (
        "project__project_name",
    )

    inlines = [AIUseCaseInline]


@admin.register(AIUseCase)
class AIUseCaseAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "assessment",
        "priority",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "priority",
    )

    search_fields = (
        "title",
        "description",
    )

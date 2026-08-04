from django.contrib import admin
from .models import Project, ProjectPhase, Milestone, LevelModule, ProjectDocument


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "project_name",
        "company",
        "project_manager",
        "status",
        "priority",
        "current_level",
        "readiness_score",
        "start_date",
        "is_active",
    )
    list_filter = ("status", "priority", "is_active")
    search_fields = ("project_name", "description")
    raw_id_fields = ("company", "project_manager")


@admin.register(ProjectPhase)
class ProjectPhaseAdmin(admin.ModelAdmin):
    list_display = ("phase_name", "project", "order", "completed")
    list_filter = ("completed",)
    raw_id_fields = ("project",)


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "due_date", "completed")
    list_filter = ("completed",)
    raw_id_fields = ("project",)


@admin.register(LevelModule)
class LevelModuleAdmin(admin.ModelAdmin):
    list_display = ("level", "title", "required_count")
    ordering = ("level",)


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "original_name",
        "project",
        "doc_type",
        "level",
        "verification_status",
        "verification_score",
        "uploaded_at",
    )
    list_filter = ("doc_type", "level", "verification_status")
    search_fields = ("original_name",)
    raw_id_fields = ("project", "uploaded_by")

from django.contrib import admin
from .models import ProjectMember


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):

    list_display = (
        "project",
        "user",
        "role",
        "is_active",
    )

    list_filter = (
        "project",
        "role",
        "is_active",
    )

    search_fields = (
        "project__project_name",
        "user__email",
    )
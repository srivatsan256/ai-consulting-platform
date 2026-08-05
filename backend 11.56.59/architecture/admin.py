from django.contrib import admin

from .models import ArchitectureDiagram, TechnologyStack


@admin.register(ArchitectureDiagram)
class ArchitectureDiagramAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "project",
        "category",
        "version",
        "created_by",
        "created_at",
    )

    list_filter = (
        "category",
    )

    search_fields = (
        "title",
        "description",
    )


@admin.register(TechnologyStack)
class TechnologyStackAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "project",
        "category",
        "version",
        "is_active",
    )

    list_filter = (
        "category",
        "is_active",
    )

    search_fields = (
        "name",
        "purpose",
    )

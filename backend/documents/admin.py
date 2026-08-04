from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "document_type",
        "project",
        "status",
        "version",
    )

    list_filter = (
        "document_type",
        "status",
    )

    search_fields = (
        "title",
        "project__project_name",
    )
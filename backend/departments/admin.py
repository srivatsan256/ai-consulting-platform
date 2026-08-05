from django.contrib import admin

from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "code",
        "company",
        "head",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "company",
    )

    search_fields = (
        "name",
        "code",
        "company__company_name",
    )

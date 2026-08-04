from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "industry",
        "email",
        "phone",
        "is_active",
    )

    search_fields = (
        "company_name",
        "industry",
    )

    list_filter = (
        "industry",
        "is_active",
    )

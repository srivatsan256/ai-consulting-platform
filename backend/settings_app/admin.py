from django.contrib import admin

from .models import SystemSetting, UserProfile


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):

    list_display = (
        "key",
        "category",
        "is_sensitive",
        "updated_by",
        "updated_at",
    )

    list_filter = (
        "category",
        "is_sensitive",
    )

    search_fields = (
        "key",
        "description",
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "timezone",
        "language",
        "theme",
    )

    search_fields = (
        "user__email",
    )

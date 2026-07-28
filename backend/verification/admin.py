from django.contrib import admin
from .models import (
    LevelModule, LevelMustInclude, LevelRecommended,
    LevelKeyPrompt, LevelRequiredDoc, LevelRequirementItem,
)


class LevelMustIncludeInline(admin.TabularInline):
    model = LevelMustInclude
    extra = 0


class LevelRecommendedInline(admin.TabularInline):
    model = LevelRecommended
    extra = 0


class LevelKeyPromptInline(admin.TabularInline):
    model = LevelKeyPrompt
    extra = 0


class LevelRequiredDocInline(admin.TabularInline):
    model = LevelRequiredDoc
    extra = 0


class LevelRequirementItemInline(admin.TabularInline):
    model = LevelRequirementItem
    extra = 0


@admin.register(LevelModule)
class LevelModuleAdmin(admin.ModelAdmin):
    list_display = ("level", "title", "icon", "color", "is_active", "order")
    list_filter = ("is_active",)
    ordering = ("level",)
    inlines = [
        LevelMustIncludeInline,
        LevelRecommendedInline,
        LevelKeyPromptInline,
        LevelRequiredDocInline,
        LevelRequirementItemInline,
    ]

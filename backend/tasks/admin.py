from django.contrib import admin

from .models import Task, TaskComment


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0
    readonly_fields = ("author", "content", "created_at")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "project",
        "status",
        "priority",
        "assigned_to",
        "due_date",
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

    inlines = [TaskCommentInline]


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):

    list_display = (
        "task",
        "author",
        "created_at",
    )

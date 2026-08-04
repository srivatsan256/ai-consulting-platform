from django.contrib import admin

from .models import Issue, IssueComment


class IssueCommentInline(admin.TabularInline):
    model = IssueComment
    extra = 0
    readonly_fields = ("author", "content", "created_at")


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "project",
        "category",
        "status",
        "priority",
        "assigned_to",
        "due_date",
    )

    list_filter = (
        "status",
        "priority",
        "category",
    )

    search_fields = (
        "title",
        "description",
    )

    inlines = [IssueCommentInline]


@admin.register(IssueComment)
class IssueCommentAdmin(admin.ModelAdmin):

    list_display = (
        "issue",
        "author",
        "created_at",
    )

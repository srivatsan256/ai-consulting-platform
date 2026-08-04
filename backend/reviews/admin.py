from django.contrib import admin

from .models import Review, ReviewComment


class ReviewCommentInline(admin.TabularInline):
    model = ReviewComment
    extra = 0
    readonly_fields = ("author", "content", "created_at")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "review_type",
        "project",
        "status",
        "reviewer",
        "rating",
        "created_at",
    )

    list_filter = (
        "status",
        "review_type",
        "rating",
    )

    search_fields = (
        "title",
        "description",
    )

    inlines = [ReviewCommentInline]


@admin.register(ReviewComment)
class ReviewCommentAdmin(admin.ModelAdmin):

    list_display = (
        "review",
        "author",
        "created_at",
    )

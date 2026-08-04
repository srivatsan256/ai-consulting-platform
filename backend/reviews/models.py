from django.db import models

from accounts.models import User
from projects.models import Project


class Review(models.Model):

    STATUS = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    REVIEW_TYPE = [
        ("design", "Design Review"),
        ("code", "Code Review"),
        ("document", "Document Review"),
        ("architecture", "Architecture Review"),
        ("security", "Security Review"),
        ("general", "General Review"),
    ]

    RATING = [
        (1, "1 - Poor"),
        (2, "2 - Below Average"),
        (3, "3 - Average"),
        (4, "4 - Good"),
        (5, "5 - Excellent"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    review_type = models.CharField(
        max_length=20,
        choices=REVIEW_TYPE,
        default="general",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending",
    )

    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reviews_assigned",
    )

    requested_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reviews_requested",
    )

    rating = models.PositiveIntegerField(
        choices=RATING,
        null=True,
        blank=True,
    )

    feedback = models.TextField(blank=True)

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reviews"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class ReviewComment(models.Model):

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="review_comments",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="review_comments",
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "review_comments"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.review}"

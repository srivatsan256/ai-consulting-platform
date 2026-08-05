from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import Review, ReviewComment
from .serializers import ReviewSerializer, ReviewCommentSerializer
from .filters import ReviewFilter


class ReviewViewSet(viewsets.ModelViewSet):

    serializer_class = ReviewSerializer

    queryset = Review.objects.select_related(
        "project",
        "reviewer",
        "requested_by",
    )

    filterset_class = ReviewFilter

    search_fields = [
        "title",
        "description",
        "feedback",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "rating",
        "status",
    ]

    ordering = ["-created_at"]

    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        review = self.get_object()
        review.status = "completed"
        review.rating = request.data.get("rating", review.rating)
        review.feedback = request.data.get("feedback", review.feedback)
        review.completed_at = timezone.now()
        review.save()
        return Response({"message": "Review completed."})

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        review = self.get_object()
        review.status = "cancelled"
        review.save()
        return Response({"message": "Review cancelled."})

    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        review = self.get_object()

        if request.method == "GET":
            comments = review.review_comments.select_related("author")
            serializer = ReviewCommentSerializer(comments, many=True)
            return Response(serializer.data)

        serializer = ReviewCommentSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(review=review)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

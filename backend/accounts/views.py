from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer
from .filters import UserFilter


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = UserFilter
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering_fields = ["email", "username", "created_at"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response(
            {"message": f"User {user.email} activated."},
            status=200,
        )

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        if user == request.user:
            return Response(
                {"detail": "You cannot deactivate your own account."},
                status=400,
            )
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response(
            {"message": f"User {user.email} deactivated."},
            status=200,
        )

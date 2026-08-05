from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

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

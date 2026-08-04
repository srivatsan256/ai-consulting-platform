from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import SystemSetting, UserProfile
from .serializers import SystemSettingSerializer, UserProfileSerializer
from .filters import SystemSettingFilter


class SystemSettingViewSet(viewsets.ModelViewSet):

    serializer_class = SystemSettingSerializer

    queryset = SystemSetting.objects.select_related("updated_by")

    filterset_class = SystemSettingFilter

    search_fields = [
        "key",
        "description",
    ]

    ordering_fields = [
        "key",
        "category",
        "created_at",
    ]

    ordering = ["category", "key"]

    permission_classes = [IsAuthenticated]


class UserProfileViewSet(viewsets.ModelViewSet):

    serializer_class = UserProfileSerializer

    queryset = UserProfile.objects.none()

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return UserProfile.objects.none()
        return UserProfile.objects.filter(
            user=self.request.user,
        ).select_related("user")

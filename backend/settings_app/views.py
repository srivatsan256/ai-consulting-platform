from django.db import models
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import SystemSetting, UserProfile, Announcement
from .serializers import SystemSettingSerializer, UserProfileSerializer, AnnouncementSerializer
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

    def get_permissions(self):
        """
        Platform settings are readable by any authenticated user but only
        writable by staff users. This prevents a tenant from tampering with
        global configuration (including sensitive values).
        """
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdminUser()]
        return super().get_permissions()


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


class AnnouncementViewSet(viewsets.ModelViewSet):

    serializer_class = AnnouncementSerializer

    permission_classes = [IsAuthenticated]

    filterset_fields = ["scope", "level", "is_active"]

    search_fields = ["title", "message"]

    ordering_fields = ["created_at", "scheduled_for", "expires_at"]

    ordering = ["-created_at"]

    lookup_value_regex = r"[0-9]+"

    def get_queryset(self):
        from django.utils import timezone

        tenant = getattr(self.request, "tenant", None)
        queryset = Announcement.objects.select_related("company", "created_by")
        if self.action == "list":
            queryset = queryset.filter(is_active=True).filter(
                models.Q(scope="global")
                | models.Q(
                    scope="tenant",
                    company=tenant.company if tenant else None,
                )
            ).filter(
                models.Q(scheduled_for__isnull=True)
                | models.Q(scheduled_for__lte=timezone.now())
            ).filter(
                models.Q(expires_at__isnull=True)
                | models.Q(expires_at__gte=timezone.now())
            )
            return queryset
        if tenant is not None and tenant.company is not None:
            queryset = queryset.filter(
                models.Q(company=tenant.company)
                | models.Q(company__isnull=True)
            )
        return queryset

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        scope = serializer.validated_data.get("scope", "tenant")
        company = serializer.validated_data.get("company")
        if scope == "tenant":
            if company and company != (tenant.company if tenant else None):
                raise PermissionDenied(
                    "You can only create announcements for your own company."
                )
            serializer.save(
                created_by=self.request.user,
                company=tenant.company if tenant else company,
            )
        else:
            if not getattr(self.request.user, "is_staff", False):
                raise PermissionDenied(
                    "Only staff users can create global announcements."
                )
            serializer.save(created_by=self.request.user)

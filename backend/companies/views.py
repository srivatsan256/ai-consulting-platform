from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.responses import success_response

from .filters import CompanyFilter
from .models import Company
from .serializers import (
    CompanyOnboardingSerializer,
    CompanySerializer,
    CompanySettingsSerializer,
)
from .services.service import CompanyService


class CompanyViewSet(ModelViewSet):
    """
    Tenant company management.

    Lists only companies the authenticated user belongs to (or all for
    staff). Status transitions are staff-only; settings, branding and
    onboarding are managed by company members.
    """

    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    filterset_class = CompanyFilter
    search_fields = ["company_name", "industry"]
    ordering_fields = ["company_name", "created_at"]
    ordering = ["company_name"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Company.objects.none()
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return Company.objects.all()
        return Company.objects.filter(members__user=user, members__is_active=True)

    def perform_create(self, serializer):
        company = serializer.save()
        from company_members.models import CompanyMember
        from roles.models import Role
        role, _ = Role.objects.get_or_create(
            role_key="company_admin",
            defaults={"display_name": "Company Admin"},
        )
        CompanyMember.objects.get_or_create(
            user=self.request.user,
            company=company,
            defaults={"role": role, "is_primary": True},
        )
        return company

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def suspend(self, request, pk=None):
        company = self.get_object()
        CompanyService.suspend(company, user=request.user)
        return success_response(
            data=CompanySerializer(company).data,
            message="Company suspended.",
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def reactivate(self, request, pk=None):
        company = self.get_object()
        CompanyService.reactivate(company, user=request.user)
        return success_response(
            data=CompanySerializer(company).data,
            message="Company reactivated.",
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def archive(self, request, pk=None):
        company = self.get_object()
        CompanyService.archive(company, user=request.user)
        return success_response(
            data=CompanySerializer(company).data,
            message="Company archived.",
        )

    @action(detail=True, methods=["get", "patch"], url_path="settings")
    def manage_settings(self, request, pk=None):
        company = self.get_object()
        if request.method == "PATCH":
            serializer = CompanySettingsSerializer(
                CompanyService.get_or_create_settings(company),
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            settings = CompanyService.update_settings(
                company, serializer.validated_data, user=request.user
            )
            return success_response(
                data=CompanySettingsSerializer(settings).data,
                message="Company settings updated.",
            )
        return success_response(
            data=CompanySettingsSerializer(
                CompanyService.get_or_create_settings(company)
            ).data
        )

    @action(detail=True, methods=["get"])
    def onboarding(self, request, pk=None):
        company = self.get_object()
        onboarding = CompanyService.get_or_create_onboarding(company)
        return success_response(data=CompanyOnboardingSerializer(onboarding).data)

    @action(detail=True, methods=["post"])
    def complete_onboarding_step(self, request, pk=None):
        company = self.get_object()
        step = request.data.get("step")
        value = request.data.get("value", True)
        onboarding = CompanyService.complete_onboarding_step(
            company, step=step, value=value, user=request.user
        )
        return success_response(
            data=CompanyOnboardingSerializer(onboarding).data,
            message="Onboarding step updated.",
        )

    @action(detail=False, methods=["get"])
    def context(self, request):
        tenant = getattr(request, "tenant", None)
        if not tenant or not tenant.company:
            return success_response(
                data=None,
                message="No company associated with this user.",
            )
        context = CompanyService.get_company_context(tenant.company)
        return success_response(
            data=CompanySerializer(context["company"]).data
            | {
                "settings": CompanySettingsSerializer(context["settings"]).data,
                "onboarding": CompanyOnboardingSerializer(context["onboarding"]).data,
            }
        )

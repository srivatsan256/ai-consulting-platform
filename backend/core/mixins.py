from rest_framework.exceptions import PermissionDenied


class CompanyQuerySetMixin:
    """
    Filters queryset by authenticated user's company.
    Uses request.tenant (TenantContext) for company resolution.
    """

    tenant_filter_enabled = True

    def get_queryset(self):
        queryset = super().get_queryset()

        if not self.tenant_filter_enabled:
            return queryset

        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()

        tenant = getattr(self.request, "tenant", None)

        if not tenant or not tenant.company:
            raise PermissionDenied("No company associated with this user.")

        return queryset.filter(company=tenant.company, is_deleted=False)

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        serializer.save(
            company=tenant.company if tenant else None,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
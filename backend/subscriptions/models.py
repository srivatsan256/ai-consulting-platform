import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class SubscriptionTier(models.TextChoices):
    STARTER = 'starter', _('Starter')
    PROFESSIONAL = 'professional', _('Professional')
    ENTERPRISE = 'enterprise', _('Enterprise')
    CUSTOM = 'custom', _('Custom')


class SubscriptionStatus(models.TextChoices):
    TRIALING = 'trialing', _('Trialing')
    ACTIVE = 'active', _('Active')
    PAST_DUE = 'past_due', _('Past Due')
    CANCELED = 'canceled', _('Canceled')
    EXPIRED = 'expired', _('Expired')


class SubscriptionPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    tier = models.CharField(
        max_length=20,
        choices=SubscriptionTier.choices,
        default=SubscriptionTier.STARTER
    )
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Feature Limits
    max_projects = models.PositiveIntegerField(default=5, help_text=_("Maximum active projects allowed"))
    max_users = models.PositiveIntegerField(default=10, help_text=_("Maximum users allowed in tenant"))
    max_storage_gb = models.PositiveIntegerField(default=10, help_text=_("Maximum document storage in GB"))
    max_ai_requests_per_month = models.PositiveIntegerField(default=1000, help_text=_("Maximum monthly RAG/AI requests"))
    
    # Feature Toggles
    allows_custom_rag = models.BooleanField(default=False)
    allows_advanced_reports = models.BooleanField(default=False)
    allows_custom_integrations = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscription_plans'
        ordering = ['price_monthly']
        verbose_name = _('Subscription Plan')
        verbose_name_plural = _('Subscription Plans')

    def __str__(self):
        return f"{self.name} ({self.get_tier_display()})"


class CompanySubscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        related_name='subscriptions',
        help_text=_("Tenant reference for multi-tenant isolation")
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='company_subscriptions'
    )
    status = models.CharField(
        max_length=20,
        choices=SubscriptionStatus.choices,
        default=SubscriptionStatus.TRIALING
    )
    trial_start_date = models.DateTimeField(null=True, blank=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField(default=timezone.now)
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'company_subscriptions'
        ordering = ['-created_at']
        verbose_name = _('Company Subscription')
        verbose_name_plural = _('Company Subscriptions')

    def __str__(self):
        return f"{self.company} - {self.plan.name} ({self.get_status_display()})"

    @property
    def is_valid(self):
        now = timezone.now()
        if self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]:
            return self.current_period_end >= now
        return False

    def has_feature(self, feature_name):
        """
        Check if a feature is enabled for this subscription's plan.
        Usage: subscription.has_feature("advanced_reports")
        """
        return getattr(self.plan, f"allows_{feature_name}", False)

    def check_limit(self, resource_name, current_count):
        """
        Check if current usage exceeds plan limits.
        Raises ValidationError if limit exceeded.
        """
        from rest_framework.exceptions import ValidationError

        limit = getattr(self.plan, f"max_{resource_name}", None)
        if limit is not None and current_count >= limit:
            raise ValidationError(
                f"{resource_name.replace('_', ' ').title()} limit of {limit} reached. "
                "Upgrade your plan to continue."
            )
        return True


class FeatureFlag(models.Model):
    """
    Platform-level feature flag.

    ``is_plan_gated`` flags are only enabled when the tenant's plan also
    grants them (``allows_<code>`` on the plan). Non-gated flags apply
    globally once active. Per-company overrides live on
    :class:`CompanyFeatureOverride`.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    is_plan_gated = models.BooleanField(
        default=True,
        help_text="Requires allows_<code> on the plan when enabled.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "feature_flags"
        ordering = ["code"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class CompanyFeatureOverride(models.Model):
    """
    Per-tenant override of a feature flag. When present it is
    authoritative for that company.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="feature_overrides",
    )
    feature = models.ForeignKey(
        FeatureFlag,
        on_delete=models.CASCADE,
        related_name="company_overrides",
    )
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "company_feature_overrides"
        unique_together = ("company", "feature")

    def __str__(self):
        return f"{self.feature.code} {'on' if self.is_enabled else 'off'} for {self.company}"


class UsageRecord(models.Model):
    """
    Monthly aggregated usage counter per company and feature/resource.

    Rows are keyed by (company, feature, month) and incremented
    atomically, keeping usage analytics bounded per month.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="usage_records",
    )
    feature = models.CharField(max_length=50, db_index=True)
    quantity = models.PositiveIntegerField(default=0)
    period_start = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "usage_records"
        unique_together = ("company", "feature", "period_start")
        ordering = ["-period_start"]

    def __str__(self):
        return f"{self.company} - {self.feature} ({self.quantity}) @ {self.period_start}"

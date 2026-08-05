from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from rest_framework.exceptions import ValidationError
from ..models import SubscriptionPlan, CompanySubscription, SubscriptionStatus


class SubscriptionService:
    @staticmethod
    def start_trial(company, plan: SubscriptionPlan, trial_days: int = 14) -> CompanySubscription:
        """
        Starts a trial period for a given company subscription.
        """
        now = timezone.now()
        trial_end = now + timedelta(days=trial_days)
        
        with transaction.atomic():
            CompanySubscription.objects.filter(
                company=company,
                status__in=[SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]
            ).update(status=SubscriptionStatus.CANCELED)

            subscription = CompanySubscription.objects.create(
                company=company,
                plan=plan,
                status=SubscriptionStatus.TRIALING,
                trial_start_date=now,
                trial_end_date=trial_end,
                current_period_start=now,
                current_period_end=trial_end
            )
        return subscription

    @staticmethod
    def upgrade_or_downgrade(subscription: CompanySubscription, new_plan: SubscriptionPlan, billing_cycle: str = 'monthly') -> CompanySubscription:
        """
        Upgrades or downgrades the company's active subscription.
        """
        now = timezone.now()
        duration_days = 365 if billing_cycle == 'yearly' else 30
        period_end = now + timedelta(days=duration_days)

        with transaction.atomic():
            subscription.plan = new_plan
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.current_period_start = now
            subscription.current_period_end = period_end
            subscription.cancel_at_period_end = False
            subscription.save()

        return subscription

    @staticmethod
    def cancel_subscription(subscription: CompanySubscription, immediate: bool = False) -> CompanySubscription:
        """
        Cancels a company subscription either immediately or at period end.
        """
        with transaction.atomic():
            if immediate:
                subscription.status = SubscriptionStatus.CANCELED
            else:
                subscription.cancel_at_period_end = True
            subscription.save()
        return subscription

    @staticmethod
    def check_feature_limit(company, feature_name: str, current_usage_count: int) -> bool:
        """
        Validates if current usage exceeds active subscription limits.
        """
        sub = CompanySubscription.objects.filter(
            company=company,
            status__in=[SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]
        ).select_related('plan').first()

        if not sub or not sub.is_valid:
            raise ValidationError("Active subscription required for this feature.")

        limit = getattr(sub.plan, f"max_{feature_name}", None)
        if limit is not None and current_usage_count >= limit:
            raise ValidationError(f"Subscription limit of {limit} for {feature_name} reached. Upgrade plan to continue.")
        
        return True

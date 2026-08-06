from django.test import TestCase
from rest_framework.exceptions import ValidationError

from companies.models import Company
from core.tests_helpers import create_company
from subscriptions.models import (
    CompanyFeatureOverride,
    FeatureFlag,
    SubscriptionPlan,
)
from subscriptions.services.feature_flag_service import FeatureFlagService
from subscriptions.services.usage_service import QuotaService, UsageService
from subscriptions.services.service import SubscriptionService


class FeatureFlagServiceTests(TestCase):

    def setUp(self):
        self.company = create_company(name="Flag Co")
        self.plan = SubscriptionPlan.objects.create(
            name="Professional",
            code="professional",
            tier="professional",
            allows_custom_rag=True,
        )
        self.subscription = SubscriptionService.start_trial(
            self.company, self.plan
        )

    def test_missing_flag_falls_back_to_plan_grant(self):
        self.assertTrue(
            FeatureFlagService.is_enabled(
                self.company, "custom_rag", subscription=self.subscription
            )
        )

    def test_missing_flag_and_plan_false_returns_false(self):
        self.assertFalse(
            FeatureFlagService.is_enabled(
                self.company, "advanced_reports", subscription=self.subscription
            )
        )

    def test_global_flag_enabled(self):
        flag = FeatureFlag.objects.create(
            code="beta_feature", name="Beta", is_plan_gated=False
        )
        self.assertTrue(
            FeatureFlagService.is_enabled(self.company, "beta_feature")
        )

    def test_inactive_global_flag_disables_feature(self):
        FeatureFlag.objects.create(
            code="beta_feature", name="Beta", is_plan_gated=False, is_active=False
        )
        self.assertFalse(
            FeatureFlagService.is_enabled(self.company, "beta_feature")
        )

    def test_override_is_authoritative(self):
        flag = FeatureFlag.objects.create(
            code="beta_feature", name="Beta", is_plan_gated=False, is_active=False
        )
        CompanyFeatureOverride.objects.create(
            company=self.company, feature=flag, is_enabled=True
        )
        self.assertTrue(
            FeatureFlagService.is_enabled(self.company, "beta_feature")
        )

    def test_feature_map_contains_all_flags(self):
        FeatureFlag.objects.create(code="alpha", name="Alpha")
        FeatureFlag.objects.create(code="beta", name="Beta")
        flags = FeatureFlagService.get_feature_map(self.company)
        self.assertIn("alpha", flags)
        self.assertIn("beta", flags)


class UsageServiceTests(TestCase):

    def setUp(self):
        self.company = create_company(name="Usage Co")

    def test_record_accumulates_within_month(self):
        UsageService.record(self.company, "ai_requests_per_month", quantity=5)
        UsageService.record(self.company, "ai_requests_per_month", quantity=3)
        self.assertEqual(
            UsageService.get_period_usage(self.company, "ai_requests_per_month"),
            8,
        )

    def test_period_usage_defaults_to_zero(self):
        self.assertEqual(
            UsageService.get_period_usage(self.company, "unknown_feature"),
            0,
        )

    def test_monthly_report_returns_period_bounds(self):
        UsageService.record(self.company, "ai_requests_per_month")
        report = UsageService.get_monthly_report(self.company)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]["feature"], "ai_requests_per_month")
        self.assertEqual(report[0]["quantity"], 1)


class QuotaServiceTests(TestCase):

    def setUp(self):
        self.company = create_company(name="Quota Co")
        self.plan = SubscriptionPlan.objects.create(
            name="Starter",
            code="starter",
            max_projects=5,
        )

    def test_check_passes_below_limit(self):
        SubscriptionService.start_trial(self.company, self.plan)
        self.assertTrue(QuotaService.check(self.company, "projects", 4))

    def test_check_raises_at_limit(self):
        SubscriptionService.start_trial(self.company, self.plan)
        with self.assertRaises(ValidationError):
            QuotaService.check(self.company, "projects", 5)

    def test_check_requires_subscription(self):
        with self.assertRaises(ValidationError):
            QuotaService.check(self.company, "projects", 1)

    def test_get_report_includes_plan_limits(self):
        SubscriptionService.start_trial(self.company, self.plan)
        report = QuotaService.get_report(self.company)
        self.assertEqual(report["plan"], "starter")
        self.assertTrue(
            any(q["resource"] == "projects" and q["limit"] == 5 for q in report["quotas"])
        )

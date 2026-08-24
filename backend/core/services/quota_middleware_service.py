"""
Quota Middleware Service
========================

Subscription quotas were removed. These stubs keep their original
signatures so views and signal handlers continue to work without
enforcing anything.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from companies.models import Company


class QuotaMiddlewareService:
    """
    Convenience façade for tenant quota checks and usage recording.
    All checks are no-ops since subscriptions were removed.
    """

    @staticmethod
    def check_project_quota(company: "Company") -> None:
        return None

    @staticmethod
    def check_user_quota(company: "Company", new_users: int = 1) -> None:
        return None

    @staticmethod
    def check_storage_quota(company: "Company", additional_bytes: int = 0) -> None:
        return None

    @staticmethod
    def check_ai_quota(company: "Company") -> None:
        return None

    @staticmethod
    def record_ai_usage(company: "Company", quantity: int = 1) -> None:
        return None

    @staticmethod
    def get_quota_summary(company: "Company") -> dict:
        return {"plan": None, "quotas": []}

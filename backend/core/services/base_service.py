import logging
from typing import Any, Dict, Optional, Type

from django.db import models, transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

logger = logging.getLogger(__name__)


class BaseService:
    """
    Reusable service layer for all tenant-aware models.
    Provides CRUD, validation, soft delete, transactions, audit, logging,
    and feature/subscription/permission enforcement.

    Usage:
        class ProjectService(BaseService):
            model = Project

            def create(self, data):
                self.require_subscription()
                self.require_feature("projects")
                return super().create(data)
    """

    model: Type[models.Model] = None
    request = None
    quota_resource: Optional[str] = None

    def __init__(self, company=None, user=None, request=None):
        self.company = company
        self.user = user
        self.request = request

    def get_queryset(self):
        return self.model.objects.filter(company=self.company, is_deleted=False)

    def get_by_id(self, pk: int) -> Optional[models.Model]:
        try:
            return self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            return None

    @transaction.atomic
    def create(self, data: Dict[str, Any]) -> models.Model:
        self.validate_create(data)
        self.check_quota()
        data["company"] = self.company
        data["created_by"] = self.user
        data["updated_by"] = self.user
        instance = self.model.objects.create(**data)
        logger.info(
            f"{self.model.__name__} created: {instance.pk} by {self.user}"
        )
        return instance

    @transaction.atomic
    def update(self, instance: models.Model, data: Dict[str, Any]) -> models.Model:
        self.validate_update(instance, data)
        data["updated_by"] = self.user
        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()
        logger.info(
            f"{self.model.__name__} updated: {instance.pk} by {self.user}"
        )
        return instance

    @transaction.atomic
    def soft_delete(self, instance: models.Model) -> models.Model:
        self.validate_delete(instance)
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save()
        logger.info(
            f"{self.model.__name__} soft deleted: {instance.pk} by {self.user}"
        )
        return instance

    @transaction.atomic
    def restore_by_id(self, pk: int) -> Optional[models.Model]:
        """
        Restore a soft-deleted instance by ID.
        """
        try:
            instance = self.model.objects.with_deleted().get(pk=pk)
            instance.is_deleted = False
            instance.deleted_at = None
            instance.save()
            logger.info(
                f"{self.model.__name__} restored: {pk} by {self.user}"
            )
            return instance
        except self.model.DoesNotExist:
            return None

    @transaction.atomic
    def delete_by_id(self, pk: int) -> Optional[models.Model]:
        """
        Soft delete by ID without requiring instance first.
        """
        instance = self.get_by_id(pk)
        if instance:
            return self.soft_delete(instance)
        return None

    @transaction.atomic
    def archive_by_id(self, pk: int) -> Optional[models.Model]:
        """
        Archive an instance by ID.
        """
        instance = self.get_by_id(pk)
        if instance:
            instance.status = "archived"
            instance.save(update_fields=["status", "updated_at"])
            logger.info(
                f"{self.model.__name__} archived: {pk} by {self.user}"
            )
            return instance
        return None

    def list(self, filters: Optional[Dict[str, Any]] = None):
        queryset = self.get_queryset()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset

    # ------------------------------------------------------------------
    # Feature / Subscription / Permission Enforcement
    # ------------------------------------------------------------------

    def require_subscription(self):
        """
        Raise PermissionDenied if no active subscription.
        """
        tenant = getattr(self.request, "tenant", None) if self.request else None
        if not tenant or not tenant.subscription:
            raise PermissionDenied("Active subscription required.")
        if not tenant.subscription.is_valid:
            raise PermissionDenied("Subscription has expired.")

    def require_feature(self, feature_name: str):
        """
        Raise PermissionDenied if feature is not enabled for the tenant.

        Delegates to the feature flag service so global flags, per-company
        overrides and plan grants are all respected.
        """
        tenant = getattr(self.request, "tenant", None) if self.request else None
        if not tenant or not tenant.company:
            raise PermissionDenied("Tenant context required.")

        from subscriptions.services.feature_flag_service import FeatureFlagService

        if not FeatureFlagService.is_enabled(
            tenant.company, feature_name, subscription=tenant.subscription
        ):
            raise PermissionDenied(
                f"Feature '{feature_name}' is not available on your current plan."
            )

    def check_quota(self):
        """
        Raise ValidationError when creating would exceed the tenant's plan
        quota for ``quota_resource``.

        Subclasses opt in by setting ``quota_resource`` and may override
        ``get_usage_count`` to count something other than all non-deleted
        rows.
        """
        if not self.quota_resource or not self.company:
            return

        from subscriptions.services.usage_service import QuotaService

        QuotaService.check(
            self.company,
            self.quota_resource,
            self.get_usage_count(),
        )

    def get_usage_count(self) -> int:
        return self.model.objects.filter(
            company=self.company,
            is_deleted=False,
        ).count()

    def require_permission(self, permission_name: str):
        """
        Raise PermissionDenied if user lacks the specified permission.
        Checks role-based permissions.
        """
        tenant = getattr(self.request, "tenant", None) if self.request else None
        if not tenant or not tenant.role:
            raise PermissionDenied("Role information required.")

        # Check if role has the permission
        from permissions.models import Permission

        has_permission = Permission.objects.filter(
            role=tenant.role,
            codename=permission_name,
        ).exists()

        if not has_permission:
            raise PermissionDenied(
                f"Permission '{permission_name}' denied for your role."
            )

    def validate_create(self, data: Dict[str, Any]):
        pass

    def validate_update(self, instance: models.Model, data: Dict[str, Any]):
        pass

    def validate_delete(self, instance: models.Model):
        pass

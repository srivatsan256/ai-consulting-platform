"""
Audit log service.

Central entry point for writing audit log records.
All auditable business operations should call AuditLogService.log instead of
creating AuditLog instances directly.
"""

from __future__ import annotations

from typing import Any, Optional

from django.db import transaction

from audit_logs.models import AuditLog


class AuditLogService:
    """
    Service responsible for persisting audit log records.
    """

    @classmethod
    @transaction.atomic
    def log(
        cls,
        *,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        resource_name: str = "",
        metadata: Optional[dict] = None,
        user: Any = None,
        company: Any = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """
        Write a single audit log record.

        Args:
            action:
                Auditable action (e.g. SESSION_CREATED, PASSWORD_CHANGED).
            resource:
                Entity type being acted on (e.g. "UserSession").
            resource_id:
                String identifier of the affected entity.
            resource_name:
                Human readable name of the affected entity.
            metadata:
                Extra structured context stored as JSON.
            user:
                User who performed the action.
            company:
                Tenant the action belongs to.
            ip_address:
                Client IP address.
            user_agent:
                Client user agent.

        Returns:
            The created AuditLog instance.
        """
        return AuditLog.objects.create(
            company=company,
            user=user,
            action=action,
            entity_type=resource,
            entity_id=resource_id or "",
            entity_name=resource_name,
            changes=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent or "",
        )

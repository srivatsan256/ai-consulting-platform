"""Notification creation service.

Views should not construct :class:`Notification` rows directly. They call
:func:`NotificationService.notify`, which respects the recipient's
:class:`NotificationPreference` toggles before creating the record.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from django.db import transaction

if TYPE_CHECKING:
    from accounts.models import User


class NotificationService:
    @staticmethod
    @transaction.atomic
    def notify(
        recipient: "User",
        title: str,
        message: str,
        notification_type: str = "info",
        category: str = "system",
        entity_type: str = "",
        entity_id: Optional[int] = None,
    ) -> Optional[object]:
        """
        Create an in-app notification for ``recipient`` unless their
        preferences disable notifications for ``category``.
        """
        from notifications.models import Notification, NotificationPreference

        if recipient is None:
            return None

        prefs, _ = NotificationPreference.objects.get_or_create(user=recipient)
        if not getattr(prefs, f"{category}_notifications", True):
            return None

        return Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            category=category,
            entity_type=entity_type,
            entity_id=entity_id,
        )

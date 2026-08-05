from django.utils import timezone

from core.logging import log_audit


def record_create(instance, user=None):
    log_audit(
        message=f"{instance.__class__.__name__} created: {instance.pk}",
        user=user,
        action="create",
        extra={
            "model": instance.__class__.__name__,
            "object_id": instance.pk,
        },
    )


def record_update(instance, user=None, changes=None):
    log_audit(
        message=f"{instance.__class__.__name__} updated: {instance.pk}",
        user=user,
        action="update",
        extra={
            "model": instance.__class__.__name__,
            "object_id": instance.pk,
            "changes": changes or {},
        },
    )


def record_delete(instance, user=None):
    log_audit(
        message=f"{instance.__class__.__name__} deleted: {instance.pk}",
        user=user,
        action="delete",
        extra={
            "model": instance.__class__.__name__,
            "object_id": instance.pk,
        },
    )


def record_soft_delete(instance, user=None):
    log_audit(
        message=f"{instance.__class__.__name__} soft deleted: {instance.pk}",
        user=user,
        action="soft_delete",
        extra={
            "model": instance.__class__.__name__,
            "object_id": instance.pk,
        },
    )


def record_login(user, ip_address=None):
    log_audit(
        message=f"User logged in: {user.email}",
        user=user,
        action="login",
        extra={
            "ip_address": ip_address,
        },
    )


def record_logout(user):
    log_audit(
        message=f"User logged out: {user.email}",
        user=user,
        action="logout",
    )


def record_permission_change(user, target_user=None, permission=None, action=None):
    log_audit(
        message=f"Permission changed: {permission} {action}",
        user=user,
        action="permission_change",
        extra={
            "target_user_id": target_user.pk if target_user else None,
            "permission": permission,
            "permission_action": action,
        },
    )


def record_password_change(user):
    log_audit(
        message=f"Password changed: {user.email}",
        user=user,
        action="password_change",
    )


def record_failed_login(email, ip_address=None):
    log_audit(
        message=f"Failed login attempt: {email}",
        action="failed_login",
        extra={
            "email": email,
            "ip_address": ip_address,
        },
    )

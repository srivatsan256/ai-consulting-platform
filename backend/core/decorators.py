import time
import functools

from django.http import JsonResponse
from rest_framework.exceptions import PermissionDenied

from core.logging import log_info, log_error, log_security


def company_required(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"error": "Authentication required."}, status=401)
        tenant = getattr(request, "tenant", None)
        if not tenant or not tenant.company:
            raise PermissionDenied("Company not assigned.")
        if not tenant.company.is_active:
            raise PermissionDenied("Company is not active.")
        return view_func(request, *args, **kwargs)
    return wrapper


def subscription_required(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        tenant = getattr(request, "tenant", None)
        if not tenant or not tenant.subscription:
            raise PermissionDenied("Active subscription required.")
        if not tenant.subscription.is_valid:
            raise PermissionDenied("Subscription has expired.")
        return view_func(request, *args, **kwargs)
    return wrapper


def feature_required(feature_name):
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            tenant = getattr(request, "tenant", None)
            if not tenant:
                raise PermissionDenied("Tenant context required.")
            from subscriptions.services.feature_flag_service import FeatureFlagService

            if not FeatureFlagService.is_enabled(
                tenant.company, feature_name, subscription=tenant.subscription
            ):
                raise PermissionDenied(f"Feature '{feature_name}' is not available.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def audit_action(action_name):
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            log_info(
                f"Audit: {action_name}",
                extra={"user": user.pk, "action": action_name},
            )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def log_execution_time(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        start = time.time()
        response = view_func(request, *args, **kwargs)
        duration = (time.time() - start) * 1000
        log_info(
            f"{view_func.__name__} executed in {duration:.2f}ms",
            extra={"duration_ms": duration},
        )
        return response
    return wrapper

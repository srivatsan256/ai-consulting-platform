"""Maintenance-mode middleware.

Reads the ``maintenance_mode`` flag from ``SystemSetting`` and serves a 503
(``service_unavailable``) response for all requests except the health check
and admin endpoints, while ``request.user`` is not a superuser.
"""

from django.db import connection
from django.http import JsonResponse


def is_maintenance_mode():
    try:
        from settings_app.models import SystemSetting

        return SystemSetting.get_value("maintenance_mode", False)
    except Exception:
        return False


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not is_maintenance_mode():
            return self.get_response(request)

        if request.path == "/api/health/":
            return self.get_response(request)

        if request.path.startswith("/admin/"):
            return self.get_response(request)

        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated and user.is_superuser:
            return self.get_response(request)

        return JsonResponse(
            {
                "success": False,
                "message": "Service is temporarily under maintenance.",
                "data": None,
                "errors": {"detail": "Maintenance mode is enabled. Please try again later."},
            },
            status=503,
        )

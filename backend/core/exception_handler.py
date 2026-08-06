from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    PermissionDenied,
    NotFound,
    ValidationError,
)
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        data = {
            "success": False,
            "message": get_message(exc),
            "data": None,
            "errors": get_errors(response.data),
        }
        return Response(data, status=response.status_code)

    return Response({
        "success": False,
        "message": "Internal server error.",
        "data": None,
        "errors": {"detail": "An unexpected error occurred."},
    }, status=500)


def get_message(exc):
    if isinstance(exc, ValidationError):
        detail = exc.detail
        if isinstance(detail, dict):
            return "; ".join(
                f"{key}: {', '.join(value) if isinstance(value, list) else value}"
                for key, value in detail.items()
            )
        if isinstance(detail, (list, tuple)):
            return ", ".join(str(item) for item in detail)
        return str(detail)
    if isinstance(exc, AuthenticationFailed):
        return "Authentication failed."
    if isinstance(exc, PermissionDenied):
        return "Permission denied."
    if isinstance(exc, NotFound):
        return "Not found."
    if isinstance(exc, APIException):
        detail = exc.detail
        if isinstance(detail, (dict, list, tuple)):
            return str(detail)
        return str(detail)
    return "An error occurred."


def get_errors(data):
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        return {"detail": data}
    return {"detail": str(data)}

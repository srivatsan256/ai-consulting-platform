"""
XSS protection middleware.

Sanitises common request fields that are frequently reflected into
responses so accidental script injection is harder to land.
"""

from __future__ import annotations

import re


_SCRIPT_RE = re.compile(
    r"<\s*/?\s*script[^>]*>",
    re.IGNORECASE,
)
_EVENT_HANDLER_RE = re.compile(
    r"\bon\w+\s*=",
    re.IGNORECASE,
)
_JS_URI_RE = re.compile(
    r"javascript\s*:",
    re.IGNORECASE,
)


def sanitize_value(value):
    """
    Strip common XSS payloads from a string-like value.
    Non-strings are returned unchanged.
    """
    if not isinstance(value, str):
        return value
    cleaned = _SCRIPT_RE.sub("", value)
    cleaned = _EVENT_HANDLER_RE.sub("", cleaned)
    cleaned = _JS_URI_RE.sub("", cleaned)
    return cleaned


def sanitize_mapping(data):
    """
    Recursively sanitise dict/list containers of string values.
    """
    if isinstance(data, dict):
        return {key: sanitize_mapping(value) for key, value in data.items()}
    if isinstance(data, list):
        return [sanitize_mapping(item) for item in data]
    return sanitize_value(data)


class XSSProtectionMiddleware:
    """
    Light-weight request sanitiser for JSON/form bodies.

    Does not replace proper output encoding; it is a defence-in-depth
    layer for multi-tenant SaaS endpoints.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Query params (immutable QueryDict) – copy only when needed.
        if request.GET:
            mutable = request.GET.copy()
            for key in list(mutable.keys()):
                values = [sanitize_value(v) for v in mutable.getlist(key)]
                mutable.setlist(key, values)
            request.GET = mutable

        if request.method in ("POST", "PUT", "PATCH") and request.POST:
            mutable = request.POST.copy()
            for key in list(mutable.keys()):
                values = [sanitize_value(v) for v in mutable.getlist(key)]
                mutable.setlist(key, values)
            request.POST = mutable

        return self.get_response(request)

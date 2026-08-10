"""
Security headers middleware.

Adds standard security-related HTTP response headers to every response.
"""


class SecurityHeadersMiddleware:
    """
    Attach defensive HTTP headers.

    Complements Django's SecurityMiddleware with API-friendly defaults
    that do not assume HTTPS-only cookie behaviour.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault("X-Content-Type-Options", "nosniff")
        response.setdefault("X-Frame-Options", "DENY")
        response.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=()",
        )
        response.setdefault("X-XSS-Protection", "0")
        return response

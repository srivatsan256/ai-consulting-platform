"""
URL configuration for AI Consulting Platform backend.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def api_root(request):
    """Welcome endpoint listing available API routes."""
    return Response(
        {
            "message": "Welcome to AI Consulting Platform API",
            "endpoints": {
                "projects": "/api/projects/",
                "admin": "/admin/",
            },
            "status": "healthy",
        }
    )


urlpatterns = [
    path("", api_root, name="api-root"),
    path("admin/", admin.site.urls),
    path("api/projects/", include("projects.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

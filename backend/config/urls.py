from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView  # type: ignore
from django.conf import settings
from django.conf.urls.static import static

# Import the password-reset views (adjust the import path if they live elsewhere)
from authentication.views import (
    PasswordResetRequestAPIView,
    PasswordResetVerifyOTPAPIView,
    PasswordResetConfirmAPIView,
)
from monitoring.views import HealthCheckAPIView

urlpatterns = [

    # Admin
    path("admin/", admin.site.urls),

    # Health check (unauthenticated)
    path("api/health/", HealthCheckAPIView.as_view(), name="health-check"),

    # Browsable API login/logout (DRF SessionAuthentication)
    path("api-auth/", include("rest_framework.urls")),

    # Authentication
    path("api/auth/", include("authentication.urls")),

    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),

    # Authentication
    path("api/accounts/", include("accounts.urls")),

    # Companies
    path("api/companies/", include("companies.urls")),

    # Company Members (membership management, switch company)
    path("api/", include("company_members.urls")),

    # Roles
    path("api/roles/", include("roles.urls")),

    # Permissions
    path("api/permissions/", include("permissions.urls")),

    # Departments
    path("api/departments/", include("departments.urls")),

    # Teams
    path("api/teams/", include("teams.urls")),

    # Projects
    path("api/projects/", include("projects.urls")),

    # Project Members
    path("api/project-members/", include("project_members.urls")),

    # Password reset
    path("password-reset/request/", PasswordResetRequestAPIView.as_view(), name="password-reset-request"),
    path("password-reset/verify-otp/", PasswordResetVerifyOTPAPIView.as_view(), name="password-reset-verify-otp"),
    path("password-reset/confirm/", PasswordResetConfirmAPIView.as_view(), name="password-reset-confirm"),

    # Discovery
    path("api/discovery/", include("discovery.urls")),

    # Documents
    path("api/documents/", include("documents.urls")),

    # Document Templates
    path("api/document-templates/", include("document_templates.urls")),

    # AI Engine
    path("api/ai-engine/", include("ai_engine.urls")),

    # Knowledge Base
    path("api/knowledge-base/", include("knowledge_base.urls")),

    # Chat
    path("api/chat/", include("chat.urls")),

    # Reviews
    path("api/reviews/", include("reviews.urls")),

    # Approvals
    path("api/approvals/", include("approvals.urls")),

    # Workflows
    path("api/workflows/", include("workflows.urls")),

    # Tasks
    path("api/tasks/", include("tasks.urls")),

    # Meetings
    path("api/meetings/", include("meetings.urls")),

    # Risks
    path("api/risks/", include("risks.urls")),

    # Issues
    path("api/issues/", include("issues.urls")),

    # Architecture
    path("api/architecture/", include("architecture.urls")),

    # Security
    path("api/security/", include("security.urls")),

    # Deployments
    path("api/deployments/", include("deployments.urls")),

    # Monitoring
    path("api/monitoring/", include("monitoring.urls")),

    # Reports
    path("api/reports/", include("reports.urls")),

    # Dashboard
    path("api/dashboard/", include("dashboard.urls")),

    # Notifications
    path("api/notifications/", include("notifications.urls")),

    # Audit Logs
    path("api/audit-logs/", include("audit_logs.urls")),

    # Integrations
    path("api/integrations/", include("integrations.urls")),

    # Settings
    path("api/settings/", include("settings_app.urls")),

    # Subscriptions
    path("api/subscriptions/", include("subscriptions.urls")),

    # Home
    path("", RedirectView.as_view(url="/api/docs/", permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
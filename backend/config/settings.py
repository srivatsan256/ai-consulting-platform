"""
Django settings for config project.
"""

from pathlib import Path
from datetime import timedelta
import os

import dj_database_url  # type: ignore

from dotenv import load_dotenv  # type: ignore


load_dotenv()


# ==========================
# Base Directory
# ==========================

BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================
# Django Core
# ==========================

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-fallback-key-change-me",
)

DEBUG = os.environ.get(
    "DJANGO_DEBUG",
    "True",
).lower() in (
    "true",
    "1",
    "yes",
)

ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost",
).split(",")


# ==========================
# Installed Applications
# ==========================

INSTALLED_APPS = [

    # Django Apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third Party
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "django_extensions",

    # Core
    "core",

    # Local Apps
    "authentication",
    "accounts",
    "companies",
    "company_members",
    "roles",
    "permissions",
    "projects",
    "project_members",
    "discovery",
    "documents",
    "departments",
    "teams",
    "document_templates",
    "reviews",
    "approvals",
    "workflows",
    "ai_engine",
    "knowledge_base",
    "chat",
    "tasks",
    "meetings",
    "risks",
    "issues",
    "architecture",
    "security",
    "deployments",
    "monitoring",
    "reports",
    "dashboard",
    "notifications",
    "audit_logs",
    "integrations",
    "settings_app",
    "subscriptions",
]


# ==========================
# Middleware
# ==========================

MIDDLEWARE = [

    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.security.SecurityMiddleware",

    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    # Multi Tenant SaaS
    "core.middleware.tenant_middleware.TenantMiddleware",

    "core.middleware.company_middleware.CompanyMiddleware",

    "core.middleware.maintenance_middleware.MaintenanceModeMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


# ==========================
# Templates
# ==========================

TEMPLATES = [

    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {

            "context_processors": [

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


# ==========================
# Database
# ==========================

DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///db.sqlite3",
        conn_max_age=600,
    )
}

if DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql":
    DATABASES["default"]["OPTIONS"] = {"connect_timeout": 10}


# ==========================
# Custom User Model
# ==========================

AUTH_USER_MODEL = "accounts.User"


# ==========================
# Password Validation
# ==========================

AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME":
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation.MinimumLengthValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation.CommonPasswordValidator",
    },

    {
        "NAME":
        "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ==========================
# Internationalization
# ==========================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# ==========================
# Static Files
# ==========================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


# ==========================
# Media Files
# ==========================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ==========================
# Django REST Framework
# ==========================

REST_FRAMEWORK = {

    "DEFAULT_AUTHENTICATION_CLASSES": (

        "authentication.services.jwt.CustomJWTAuthentication",

        "rest_framework.authentication.SessionAuthentication",

    ),

    "DEFAULT_PERMISSION_CLASSES": (

        "rest_framework.permissions.IsAuthenticated",

    ),

    "DEFAULT_PAGINATION_CLASS":

        "core.pagination.StandardPagination",

    "PAGE_SIZE":

        20,

    "EXCEPTION_HANDLER":

        "core.exception_handler.custom_exception_handler",

    "DEFAULT_THROTTLE_CLASSES": (

        "rest_framework.throttling.AnonRateThrottle",

        "rest_framework.throttling.UserRateThrottle",

    ),

    "DEFAULT_THROTTLE_RATES": {

        "anon": os.environ.get("THROTTLE_ANON_RATE", "120/min"),

        "user": os.environ.get("THROTTLE_USER_RATE", "5000/day"),

    },

    "DEFAULT_SCHEMA_CLASS":

        "drf_spectacular.openapi.AutoSchema",

    "DEFAULT_FILTER_BACKENDS": (

        "django_filters.rest_framework.DjangoFilterBackend",

        "rest_framework.filters.SearchFilter",

        "rest_framework.filters.OrderingFilter",

    ),
}


# ==========================
# JWT Configuration
# ==========================

SIMPLE_JWT = {

    "ACCESS_TOKEN_LIFETIME":
        timedelta(minutes=30),

    "REFRESH_TOKEN_LIFETIME":
        timedelta(days=7),

    "ROTATE_REFRESH_TOKENS":
        True,

    "BLACKLIST_AFTER_ROTATION":
        True,

    "UPDATE_LAST_LOGIN":
        True,

    "ALGORITHM":
        "HS256",

    "SIGNING_KEY":
        SECRET_KEY,

    "AUTH_HEADER_TYPES":
        ("Bearer",),
}

# Maximum number of concurrent active sessions allowed per user per company.
# Overridable at runtime via SystemSetting ``auth.max_concurrent_sessions``.
MAX_CONCURRENT_SESSIONS = int(
    os.environ.get("MAX_CONCURRENT_SESSIONS", "5")
)


# ==========================
# Swagger / OpenAPI
# ==========================

SPECTACULAR_SETTINGS = {

    "TITLE":
        "AI Consulting Platform API",

    "DESCRIPTION":
        "Enterprise AI Consulting Delivery Platform",

    "VERSION":
        "1.0.0",

    "SERVE_INCLUDE_SCHEMA":
        False,

    "ENUM_NAME_OVERRIDES": {
        "MaturityLevelEnum": [
            (1, "Level 1 - Initial"),
            (2, "Level 2 - Managed"),
            (3, "Level 3 - Defined"),
            (4, "Level 4 - Quantitatively Managed"),
            (5, "Level 5 - Optimizing"),
        ],
        "MonitoringSeverityEnum": [
            ("info", "Info"),
            ("warning", "Warning"),
            ("critical", "Critical"),
        ],
        "SeverityEnum": [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
    },
}


# ==========================
# CORS
# ==========================

CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://[::1]:3000,http://[::1]:5173"
    ),
).split(",")


CORS_ALLOW_CREDENTIALS = True

# During local development, accept any origin so the frontend works no matter
# which localhost host/port the Vite dev server is reached on. Production
# keeps the explicit CORS_ALLOWED_ORIGINS list above.
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True


# ==========================
# Email Configuration
# ==========================

EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)

EMAIL_HOST = os.environ.get(
    "EMAIL_HOST",
    "",
)

EMAIL_PORT = int(
    os.environ.get("EMAIL_PORT") or "587"
)

EMAIL_HOST_USER = os.environ.get(
    "EMAIL_HOST_USER",
    "",
)

EMAIL_HOST_PASSWORD = os.environ.get(
    "EMAIL_HOST_PASSWORD",
    "",
)

EMAIL_USE_TLS = os.environ.get(
    "EMAIL_USE_TLS",
    "False",
).lower() in (
    "true",
    "1",
    "yes",
)

DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    "noreply@ai-consulting-platform.com",
)


# ==========================
# Frontend URL
# ==========================

FRONTEND_URL = os.environ.get(
    "FRONTEND_URL",
    "http://localhost:3000",
)


# ==========================
# Security Headers
# ==========================

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_REFERRER_POLICY = "same-origin"

# Browser XSS filter header (best effort; CSP recommended for production).
SECURE_BROWSER_XSS_FILTER = True

SECURE_SSL_REDIRECT = os.environ.get(
    "SECURE_SSL_REDIRECT",
    "False",
).lower() in ("true", "1", "yes")

if SECURE_SSL_REDIRECT:
    SECURE_HSTS_SECONDS = int(
        os.environ.get("SECURE_HSTS_SECONDS", "31536000")
    )
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# ==========================
# Logging
# ==========================

import os as _os

_LOG_DIR = _os.path.join(BASE_DIR, "logs")
_os.makedirs(_LOG_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": _os.path.join(_LOG_DIR, "django.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "filters": ["require_debug_false"],
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}
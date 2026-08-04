from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"
    verbose_name = "Authentication"

    def ready(self):
        try:
            import authentication.signals  # type: ignore # noqa: F401
        except ImportError:
            pass
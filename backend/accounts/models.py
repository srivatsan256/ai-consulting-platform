from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model for authentication.
    """

    email = models.EmailField(unique=True)

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    designation = models.CharField(
        max_length=100,
        blank=True,
    )

    is_email_verified = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    password_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "When the password was last changed. Tokens issued before this "
            "timestamp are rejected."
        ),
    )

    password_version = models.PositiveSmallIntegerField(
        default=0,
        help_text=(
            "Incremented on every password change. JWTs carry the version "
            "they were issued with; tokens with a stale version are rejected."
        ),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "username",
    ]

    def set_password(self, raw_password) -> None:
        """
        Record when the password is set/changed and bump the JWT version.

        Existing JWTs are invalidated by comparing the token `pwd_ver` claim
        against `password_version` (see jwt.py). The version avoids relying
        on the second-granularity `iat` claim, which is ambiguous when a
        password is changed in the same second it was set.
        """
        self.password_changed_at = timezone.now()
        self.password_version += 1
        super().set_password(raw_password)

    def save(self, *args, **kwargs) -> None:
        """
        Initialize password_changed_at when a user is first created.

        Django's UserManager writes the password hash directly (bypassing
        set_password), so creation needs the timestamp set here. Fresh users
        start at password_version=0, which matches tokens issued at first
        login.
        """
        if self._state.adding and self.password_changed_at is None:
            self.password_changed_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.email
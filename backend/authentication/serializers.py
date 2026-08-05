from __future__ import annotations

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer  # type: ignore

from accounts.models import User
from authentication.models.login_history import LoginHistory
from authentication.services.login_history import LoginHistoryService
from companies.models import Company
from company_members.models import CompanyMember
from roles.models import Role



class CurrentUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        source="get_full_name",
        read_only=True,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "is_active",
        ]


class RegisterSerializer(serializers.Serializer):
    """
    Serializer for self-service account registration.

    ``account_type`` controls the default role and company:
      - ``consultant`` -> joins the consulting firm as a Company Admin
      - ``client``     -> creates (or joins) a client company as Client Admin
    """

    ACCOUNT_TYPE_CHOICES = [
        ("consultant", "Consultant"),
        ("client", "Client"),
    ]

    CONSULTING_COMPANY_NAME = "RequirementAI Consulting"

    first_name = serializers.CharField(
        max_length=150,
    )
    last_name = serializers.CharField(
        max_length=150,
    )
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )
    account_type = serializers.ChoiceField(
        choices=ACCOUNT_TYPE_CHOICES,
    )
    company_name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )

    def validate_email(self, value: str) -> str:
        """
        Normalize email and reject duplicates.
        """
        value = value.strip().lower()

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value

    def validate(self, attrs: dict) -> dict:
        """
        Validate password confirmation and account-type requirements.
        """
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {
                    "confirm_password": [
                        "Passwords do not match.",
                    ]
                }
            )

        validate_password(attrs["password"])

        if (
            attrs["account_type"] == "client"
            and not (attrs.get("company_name") or "").strip()
        ):
            raise serializers.ValidationError(
                {
                    "company_name": [
                        "Company name is required for client accounts.",
                    ]
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data: dict) -> dict:
        """
        Create the user, company membership and default role.
        """
        email = validated_data["email"]
        account_type = validated_data["account_type"]

        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=validated_data["first_name"].strip(),
            last_name=validated_data["last_name"].strip(),
            password=validated_data["password"],
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )

        if account_type == "client":
            company, _ = Company.objects.get_or_create(
                company_name=validated_data["company_name"].strip(),
                defaults={
                    "industry": "",
                    "business_description": "",
                },
            )
            role, _ = Role.objects.get_or_create(
                role_key="client_admin",
                defaults={"display_name": "Client Admin"},
            )
        else:
            company, _ = Company.objects.get_or_create(
                company_name=self.CONSULTING_COMPANY_NAME,
                defaults={
                    "industry": "Consulting",
                    "business_description": (
                        "AI consulting delivery platform operator."
                    ),
                },
            )
            role, _ = Role.objects.get_or_create(
                role_key="company_admin",
                defaults={"display_name": "Company Admin"},
            )

        CompanyMember.objects.get_or_create(
            user=user,
            company=company,
            defaults={
                "role": role,
                "is_primary": True,
                "is_active": True,
            },
        )

        return {
            "user": user,
            "company": {
                "id": company.id,
                "name": company.company_name,
            },
            "role": {
                "id": role.id,
                "name": role.display_name,
                "key": role.role_key,
            },
        }


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer.
    Adds company_id and user information into JWT claims.
    """

    username_field = User.USERNAME_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        membership = (
            CompanyMember.objects
            .filter(
                user=user,
                is_active=True,
                is_primary=True,
            )
            .select_related("company", "role")
            .first()
        )

        if membership:
            token["company_id"] = membership.company_id
            token["role_id"] = membership.role_id
            token["company_name"] = membership.company.company_name

        token["email"] = user.email
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name

        token["pwd_ver"] = getattr(user, "password_version", 0)

        return token

    def validate(self, attrs):
        request = self.context.get("request")

        try:
            data = super().validate(attrs)
        except AuthenticationFailed:
            LoginHistoryService.record_login_failed(
                request=request,
                email=attrs.get(self.username_field, ""),
            )
            raise

        user = self.user

        if request is not None:
            LoginHistoryService.record_login_success(
                request=request,
                user=user,
            )
            self._create_session(request, user, data.get("refresh", ""))

        membership = (
            CompanyMember.objects
            .filter(
                user=self.user,
                is_active=True,
                is_primary=True,
            )
            .select_related("company", "role")
            .first()
        )

        data["user"] = CurrentUserSerializer(self.user).data

        if membership:
            data["company"] = {
                "id": membership.company.id,
                "name": membership.company.company_name,
            }

            data["role"] = {
                "id": membership.role.id if membership.role else None,
                "name": membership.role.display_name if membership.role else None,
                "key": membership.role.role_key if membership.role else None,
            }

        return data

    def _create_session(self, request, user, refresh_token):
        """
        Persist a UserSession for the newly issued refresh token.
        """

        from datetime import datetime, timezone as tz

        from rest_framework_simplejwt.tokens import RefreshToken

        from authentication.services.device_info import parse_user_agent
        from authentication.services.session_service import SessionService

        if not refresh_token:
            return

        refresh = RefreshToken(refresh_token)

        membership = (
            CompanyMember.objects
            .filter(
                user=user,
                is_active=True,
                is_primary=True,
            )
            .select_related("company")
            .first()
        )

        if membership is None:
            return

        user_agent = LoginHistoryService.get_user_agent(request)
        browser, operating_system, device_type = parse_user_agent(user_agent)

        SessionService.create_session(
            user=user,
            company=membership.company,
            refresh_token_jti=refresh["jti"],
            expires_at=datetime.fromtimestamp(
                refresh["exp"],
                tz=tz.utc,
            ),
            ip_address=LoginHistoryService.get_client_ip(request),
            user_agent=user_agent,
            browser=browser,
            operating_system=operating_system,
            device_name=browser or device_type or "Unknown Device",
            device_type=device_type,
        )


class LoginSerializer(serializers.Serializer):
    """
    Optional login serializer if you need custom login endpoint.
    """

    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            username=email,
            password=password,
        )

        if user is None:
            raise AuthenticationFailed("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationFailed("User account is inactive.")

        attrs["user"] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        required=True,
        write_only=True,
    )

    new_password = serializers.CharField(
        required=True,
        write_only=True,
    )

    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
    )

    def validate(self, attrs):
        user = self.context["request"].user

        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError(
                {"old_password": "Old password is incorrect."}
            )

        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        validate_password(attrs["new_password"], user)

        return attrs


class SwitchCompanySerializer(serializers.Serializer):
    company_id = serializers.IntegerField()


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset email.
    """

    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        """
        Normalize email before processing.
        """
        return value.strip().lower()


class PasswordResetVerifyOTPSerializer(serializers.Serializer):
    """
    Serializer for verifying a password reset OTP.
    """

    email = serializers.EmailField()

    otp = serializers.CharField(
        max_length=6,
        min_length=6,
        help_text="6-digit one-time password sent to the user's email.",
    )

    def validate_email(self, value: str) -> str:
        """
        Normalize email before processing.
        """
        return value.strip().lower()

    def validate_otp(self, value: str) -> str:
        """
        Ensure the OTP only contains digits.
        """
        if not value.isdigit():
            raise serializers.ValidationError(
                "OTP must contain only digits."
            )
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming password reset.
    """

    uid = serializers.CharField()
    token = serializers.CharField()

    new_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs: dict) -> dict:
        """
        Validate password fields.
        """
        password = attrs["new_password"]
        confirm_password = attrs["confirm_password"]

        if password != confirm_password:
            raise serializers.ValidationError(
                {
                    "confirm_password": [
                        "Passwords do not match."
                    ]
                }
            )

        validate_password(password)

        return attrs


class EmailVerificationRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting email verification link.
    """

    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        """
        Normalize email address.
        """
        return value.strip().lower()


class EmailVerificationConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming email verification.
    """

    uid = serializers.CharField()
    token = serializers.CharField()
class LoginHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for login history records.
    """

    user_email = serializers.SerializerMethodField()

    def get_user_email(self, obj) -> str | None:
        user = getattr(obj, "user", None)
        if user is None:
            return None
        return user.email

    company_name = serializers.SerializerMethodField()

    def get_company_name(self, obj) -> str | None:
        company = getattr(obj, "company", None)
        if company is None:
            return None
        return company.company_name

    class Meta:
        model = LoginHistory
        fields = (
            "id",
            "user",
            "user_email",
            "company",
            "company_name",
            "event_type",
            "ip_address",
            "user_agent",
            "created_at",
        )

        read_only_fields = fields
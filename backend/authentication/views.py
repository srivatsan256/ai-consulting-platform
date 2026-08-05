from rest_framework import status, viewsets
from rest_framework import filters, serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend  # type: ignore
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError  # type: ignore
from rest_framework_simplejwt.views import TokenObtainPairView  # type: ignore

from authentication.models.login_history import LoginHistory
from authentication.permissions import CanViewLoginHistory
from authentication.serializers import LoginHistorySerializer

from authentication.serializers import (
    ChangePasswordSerializer,
    CurrentUserSerializer,
    CustomTokenObtainPairSerializer,
    EmailVerificationConfirmSerializer,
    EmailVerificationRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    PasswordResetVerifyOTPSerializer,
    RegisterSerializer,
    SwitchCompanySerializer,
)
from authentication.services.email_verification_service import EmailVerificationService
from authentication.services.jwt import CustomTokenRefreshSerializer
from authentication.services.password_reset_service import PasswordResetService
from authentication.services.service import AuthenticationService


class RegisterAPIView(APIView):
    """
    POST /api/auth/register/

    Creates a user account (consultant or client) and returns JWT tokens
    so the user is signed in immediately after registering.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            import json as _json

            print("REGISTER-DEBUG body:", _json.dumps(request.data)[:1000])
            print("REGISTER-DEBUG errors:", _json.dumps(serializer.errors)[:1000])
            raise serializers.ValidationError(serializer.errors)

        result = serializer.create(serializer.validated_data)
        user = result["user"]

        service = AuthenticationService(request)
        tokens = service.create_tokens(user)

        try:
            EmailVerificationService.send_verification_email(
                email=user.email,
            )
        except Exception:
            pass

        return Response(
            {
                "success": True,
                "message": "Account created successfully.",
                "refresh": tokens["refresh"],
                "access": tokens["access"],
                "user": CurrentUserSerializer(user).data,
                "company": result["company"],
                "role": result["role"],
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(TokenObtainPairView):
    """
    POST /api/auth/login/
    """
    serializer_class = CustomTokenObtainPairSerializer


class RefreshTokenAPIView(APIView):
    """
    POST /api/auth/refresh/
    """
    serializer_class = CustomTokenRefreshSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomTokenRefreshSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(exc.args[0])

        return Response(
            {
                "success": True,
                "message": "Token refreshed successfully.",
                "data": serializer.validated_data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutAPIView(APIView):
    """
    POST /api/auth/logout/
    """
    serializer_class = CustomTokenRefreshSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {
                    "success": False,
                    "message": "Refresh token is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = AuthenticationService(request)
        service.logout(refresh_token)

        return Response(
            {
                "success": True,
                "message": "Logout successful.",
            },
            status=status.HTTP_200_OK,
        )


class CurrentUserAPIView(APIView):
    """
    GET /api/auth/me/
    """
    serializer_class = CurrentUserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = AuthenticationService(request)
        serializer = CurrentUserSerializer(service.get_current_user())
        membership = service.get_primary_membership()

        data = serializer.data

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

        return Response(
            {
                "success": True,
                "data": data,
            }
        )


class ChangePasswordAPIView(APIView):
    """
    POST /api/auth/change-password/
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        service = AuthenticationService(request)
        service.change_password(serializer)

        return Response(
            {
                "success": True,
                "message": "Password changed successfully.",
            }
        )


class SwitchCompanyAPIView(APIView):
    """
    POST /api/auth/switch-company/
    """
    serializer_class = SwitchCompanySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SwitchCompanySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = AuthenticationService(request)
        membership = service.switch_company(
            serializer.validated_data["company_id"]
        )
        tokens = service.create_tokens(request.user)

        return Response(
            {
                "success": True,
                "message": "Company switched successfully.",
                "company": {
                    "id": membership.company.id,
                    "name": membership.company.company_name,
                },
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestAPIView(APIView):
    """
    POST /api/auth/password-reset/request/
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        PasswordResetService.request_password_reset_otp(
            email=serializer.validated_data["email"]
        )

        return Response(
            {
                "success": True,
                "message": (
                    "If an account with that email exists, a password reset "
                    "OTP has been sent."
                ),
                "data": {},
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetVerifyOTPAPIView(APIView):
    """
    POST /api/auth/password-reset/verify-otp/
    """
    serializer_class = PasswordResetVerifyOTPSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetVerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid, token = PasswordResetService.verify_otp(
                email=serializer.validated_data["email"],
                otp=serializer.validated_data["otp"],
            )
        except ValueError as exc:
            return Response(
                {
                    "success": False,
                    "message": str(exc),
                    "errors": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "success": True,
                "message": "OTP verified successfully.",
                "data": {
                    "uid": uid,
                    "token": token,
                },
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmAPIView(APIView):
    """
    POST /api/auth/password-reset-confirm/
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            PasswordResetService.reset_password(
                uid=serializer.validated_data["uid"],
                token=serializer.validated_data["token"],
                new_password=serializer.validated_data["new_password"],
            )

            return Response(
                {
                    "success": True,
                    "message": "Password has been reset successfully.",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as exc:
            return Response(
                {
                    "success": False,
                    "message": str(exc),
                    "errors": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class EmailVerificationRequestAPIView(APIView):
    """
    POST /api/auth/email-verification/
    """
    serializer_class = EmailVerificationRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = EmailVerificationRequestSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        EmailVerificationService.send_verification_email(
            email=serializer.validated_data["email"],
        )

        return Response(
            {
                "success": True,
                "message": (
                    "If the account exists, a verification email "
                    "has been sent."
                ),
                "data": {},
            },
            status=status.HTTP_200_OK,
        )


class EmailVerificationConfirmAPIView(APIView):
    """
    GET /api/auth/email-verification-confirm/
    """
    serializer_class = EmailVerificationConfirmSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        serializer = EmailVerificationConfirmSerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=True)

        try:
            EmailVerificationService.verify_email(
                uid=serializer.validated_data["uid"],
                token=serializer.validated_data["token"],
            )

            return Response(
                {
                    "success": True,
                    "message": "Email verified successfully.",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as exc:
            return Response(
                {
                    "success": False,
                    "message": str(exc),
                    "errors": {},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
class LoginHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for viewing authentication history.
    """

    serializer_class = LoginHistorySerializer
    permission_classes = [
        IsAuthenticated,
        CanViewLoginHistory,
    ]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "event_type",
        "company",
        "user",
    ]

    search_fields = [
        "user__email",
        "ip_address",
        "user_agent",
    ]

    ordering_fields = [
        "created_at",
        "event_type",
    ]

    ordering = [
        "-created_at",
    ]

    def get_queryset(self):
        """
        Return login history for the current tenant only.
        """

        from company_members.models import CompanyMember

        if getattr(self, "swagger_fake_view", False):
            return LoginHistory.objects.none()

        queryset = (
            LoginHistory.objects.select_related(
                "user",
                "company",
            )
            .all()
        )

        user = self.request.user

        # Super Admin can view all companies.
        if user.is_superuser:
            return queryset

        membership = CompanyMember.objects.primary_for_user(user)

        if membership is None:
            return queryset.none()

        return queryset.filter(company=membership.company)

    def list(self, request, *args, **kwargs):
        """
        Return paginated login history.
        """

        response = super().list(request, *args, **kwargs)

        return Response(
            {
                "success": True,
                "message": "Login history retrieved successfully.",
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Return a single login history record.
        """

        response = super().retrieve(request, *args, **kwargs)

        return Response(
            {
                "success": True,
                "message": "Login history retrieved successfully.",
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )
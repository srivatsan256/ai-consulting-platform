from django.urls import include, path
from rest_framework.routers import DefaultRouter

from authentication.views import (
    ChangePasswordAPIView,
    CurrentUserAPIView,
    EmailVerificationConfirmAPIView,
    EmailVerificationRequestAPIView,
    LoginAPIView,
    LoginHistoryViewSet,  # Ensure this is imported
    LogoutAPIView,
    PasswordResetConfirmAPIView,
    PasswordResetRequestAPIView,
    PasswordResetVerifyOTPAPIView,
    RefreshTokenAPIView,
    RegisterAPIView,
    SessionViewSet,
    SwitchCompanyAPIView,
)

app_name = "authentication"

# Initialize DRF Router for ViewSets
router = DefaultRouter()
router.register(r"login-history", LoginHistoryViewSet, basename="login-history")
router.register(r"sessions", SessionViewSet, basename="session")

urlpatterns = [
    # Router URLs (Login History ViewSet)
    path("", include(router.urls)),
    
    # Authentication
    path("login/", LoginAPIView.as_view(), name="login"),
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("refresh/", RefreshTokenAPIView.as_view(), name="token_refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),

    # Email Verification
    path("email-verification/request/", EmailVerificationRequestAPIView.as_view(), name="email-verification-request"),
    path("email-verification/confirm/", EmailVerificationConfirmAPIView.as_view(), name="email-verification-confirm"),

    # User
    path("me/", CurrentUserAPIView.as_view(), name="current_user"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change_password"),

    # Password Reset
    path("password-reset/request/", PasswordResetRequestAPIView.as_view(), name="password-reset-request"),
    path("password-reset/verify-otp/", PasswordResetVerifyOTPAPIView.as_view(), name="password-reset-verify-otp"),
    path("password-reset/confirm/", PasswordResetConfirmAPIView.as_view(), name="password-reset-confirm"),

    # Company
    path("switch/", SwitchCompanyAPIView.as_view(), name="switch_company"),
]
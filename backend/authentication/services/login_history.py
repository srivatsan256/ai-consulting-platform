"""
Service layer for Login History.

This service is responsible for recording authentication events.
All authentication views/services should use this service instead
of directly creating LoginHistory records.
"""

from __future__ import annotations

from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpRequest

from authentication.models.login_history import LoginHistory
from companies.models import Company
from company_members.models import CompanyMember

LoginEventType = LoginHistory.EventType

User = get_user_model()


class LoginHistoryService:
    """
    Service responsible for creating login history records.
    """

    @staticmethod
    def get_client_ip(request: Optional[HttpRequest]) -> str:
        """
        Return the client's IP address.

        Supports deployments behind reverse proxies/load balancers.
        """
        if request is None:
            return "0.0.0.0"

        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        return request.META.get("REMOTE_ADDR", "0.0.0.0")

    @staticmethod
    def get_user_agent(request: Optional[HttpRequest]) -> str:
        """
        Return the request User-Agent.
        """
        if request is None:
            return ""

        return request.META.get("HTTP_USER_AGENT", "")[:2000]

    @classmethod
    @transaction.atomic
    def record_event(
        cls,
        *,
        request: HttpRequest,
        event_type: LoginEventType,
        user: Optional[User] = None,
        company: Optional[Company] = None,
        email: str = "",
    ) -> LoginHistory:
        """
        Record an authentication event.

        Args:
            request:
                Current HTTP request.
            event_type:
                Authentication event.
            user:
                Authenticated user (None for failed login).
            company:
                Tenant company.
            email:
                Email entered during login.
                Useful for failed authentication attempts.

        Returns:
            LoginHistory instance.
        """
        if user and company is None:
            membership = CompanyMember.objects.primary_for_user(user)
            if membership:
                company = membership.company

        return LoginHistory.objects.create(
            user=user,
            company=company,
            event_type=event_type,
            ip_address=cls.get_client_ip(request),
            user_agent=cls.get_user_agent(request),
            email=email or "",
        )

    @classmethod
    def record_login_success(
        cls,
        *,
        request: HttpRequest,
        user: User,
        company: Optional[Company] = None,
    ) -> LoginHistory:
        """
        Record a successful login.
        """
        return cls.record_event(
            request=request,
            event_type=LoginEventType.LOGIN_SUCCESS,
            user=user,
            company=company,
            email=user.email,
        )

    @classmethod
    def record_login_failed(
        cls,
        *,
        request: HttpRequest,
        email: str,
        company: Optional[Company] = None,
    ) -> LoginHistory:
        """
        Record a failed authentication attempt.
        """
        return cls.record_event(
            request=request,
            event_type=LoginEventType.LOGIN_FAILED,
            company=company,
            email=email,
        )

    @classmethod
    def record_logout(
        cls,
        *,
        request: HttpRequest,
        user: User,
        company: Optional[Company] = None,
    ) -> LoginHistory:
        """
        Record a logout event.
        """
        return cls.record_event(
            request=request,
            event_type=LoginEventType.LOGOUT,
            user=user,
            company=company,
            email=user.email,
        )
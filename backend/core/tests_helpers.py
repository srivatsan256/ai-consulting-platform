"""Shared helpers for the project's test suite.

Convention note: this module intentionally does not start with ``test`` so
Django's test runner does not attempt to collect it as a test module.
"""

from django.contrib.auth import get_user_model

from companies.models import Company
from company_members.models import CompanyMember
from roles.models import Role

from datetime import date


User = get_user_model()


def create_user(username="probe", email="probe@example.com", **kwargs):
    return User.objects.create_user(
        username=username,
        email=email,
        password="Password@123",
        **kwargs,
    )


def create_superuser(username="root", email="root@example.com", **kwargs):
    return User.objects.create_superuser(
        username=username,
        email=email,
        password="AdminPass@123",
        **kwargs,
    )


def create_company(name="Acme Corp", **kwargs):
    return Company.objects.create(
        company_name=name,
        industry="Technology",
        **kwargs,
    )


def get_role(role_key="company_admin", display_name="Company Admin"):
    role, _ = Role.objects.get_or_create(
        role_key=role_key,
        defaults={"display_name": display_name},
    )
    return role


def create_member(user, company, role_key="company_admin", is_primary=True, **kwargs):
    return CompanyMember.objects.create(
        user=user,
        company=company,
        role=get_role(role_key),
        is_primary=is_primary,
        **kwargs,
    )


def create_project(company, name="Test Project", **kwargs):
    from projects.models import Project

    defaults = {
        "project_name": name,
        "company": company,
        "start_date": date(2025, 1, 1),
    }
    defaults.update(kwargs)
    return Project.objects.create(**defaults)


def authenticate(client, user):
    """Authenticate a test client via a real JWT so the full auth + tenant
    resolution path (including ``request.tenant``) is exercised."""
    from rest_framework_simplejwt.tokens import RefreshToken

    access = RefreshToken.for_user(user).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

"""
Tenant Context

Provides request-local storage for the current tenant (Company)
using ContextVar.

This ensures tenant information is isolated per request and is
safe for both synchronous and asynchronous execution.
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from companies.models import Company


_current_tenant: ContextVar[Optional["Company"]] = ContextVar(
    "current_tenant",
    default=None,
)


def set_current_tenant(company: Optional["Company"]) -> None:
    """
    Store the current tenant for the active request.

    Args:
        company:
            The authenticated user's company.
    """
    _current_tenant.set(company)


def get_current_tenant() -> Optional["Company"]:
    """
    Return the current tenant.

    Returns:
        Company | None
    """
    return _current_tenant.get()


def clear_current_tenant() -> None:
    """
    Remove the tenant from the current request context.
    """
    _current_tenant.set(None)


def has_current_tenant() -> bool:
    """
    Check whether a tenant exists in the current context.

    Returns:
        bool
    """
    return get_current_tenant() is not None
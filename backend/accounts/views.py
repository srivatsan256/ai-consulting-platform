import csv
import io
import secrets

from django.db import transaction
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from company_members.models import CompanyMember
from core.rbac.permissions import is_manager_role
from roles.models import Role

from .models import User
from .serializers import UserSerializer
from .filters import UserFilter


def _tenant_company(request):
    tenant = getattr(request, "tenant", None)
    return getattr(tenant, "company", None)


def _parse_bool(value, default=True):
    if isinstance(value, bool):
        return value
    if value is None or value == "":
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "y", "on")


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = UserFilter
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering_fields = ["email", "username", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if getattr(user, "is_superuser", False):
            return queryset
        tenant = getattr(self.request, "tenant", None)
        company = getattr(tenant, "company", None)
        if company is None:
            return queryset.none()
        queryset = queryset.filter(company_memberships__company=company)
        if self.action == "list":
            queryset = queryset.filter(company_memberships__is_active=True)
        return queryset.distinct()

    def perform_create(self, serializer):
        user = serializer.save()
        tenant = getattr(self.request, "tenant", None)
        company = getattr(tenant, "company", None)
        if company is not None:
            from roles.models import Role
            role, _ = Role.objects.get_or_create(
                role_key="consultant",
                defaults={"display_name": "Consultant"},
            )
            CompanyMember.objects.get_or_create(
                user=user,
                company=company,
                defaults={"role": role},
            )
        return user

    # ------------------------------------------------------------------
    # Authorization helpers
    # ------------------------------------------------------------------

    def _tenant_company(self):
        return _tenant_company(self.request)

    def _can_manage(self, company):
        user = self.request.user
        if getattr(user, "is_superuser", False):
            return True
        if company is None:
            return False
        membership = (
            CompanyMember.objects.filter(
                user=user,
                company=company,
                is_active=True,
            )
            .select_related("role")
            .first()
        )
        return membership is not None and is_manager_role(membership.role)

    def _require_manager(self):
        company = self._tenant_company()
        if not self._can_manage(company):
            return None
        return company

    # ------------------------------------------------------------------
    # Activation / deactivation
    # ------------------------------------------------------------------

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        user = self.get_object()
        company = self._tenant_company()
        if not self._can_manage(company):
            return Response(
                {"detail": "Only company managers can activate users."},
                status=403,
            )
        if user.is_superuser and not request.user.is_superuser: # type: ignore
            return Response(
                {"detail": "You cannot activate a platform superuser."},
                status=403,
            )
        user.is_active = True
        user.save(update_fields=["is_active"])
        if company is not None:
            CompanyMember.objects.filter(
                user=user,
                company=company,
            ).update(is_active=True)
        return Response(
            {"message": f"User {user.email} activated."},
            status=200,
        )

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        if user == request.user:
            return Response(
                {"detail": "You cannot deactivate your own account."},
                status=400,
            )
        company = self._tenant_company()
        if not self._can_manage(company):
            return Response(
                {"detail": "Only company managers can deactivate users."},
                status=403,
            )
        if user.is_superuser and not request.user.is_superuser: # type: ignore
            return Response(
                {"detail": "You cannot deactivate a platform superuser."},
                status=403,
            )
        user.is_active = False
        user.save(update_fields=["is_active"])
        if company is not None:
            CompanyMember.objects.filter(
                user=user,
                company=company,
            ).update(is_active=False)
        return Response(
            {"message": f"User {user.email} deactivated."},
            status=200,
        )

    # ------------------------------------------------------------------
    # Bulk import / export
    # ------------------------------------------------------------------

    @action(detail=False, methods=["post"], url_path="bulk-import", url_name="bulk-import")
    def bulk_import(self, request):
        """
        Import users in bulk for the acting company.

        Accepts either a JSON payload ``{"users": [{"email", "first_name",
        "last_name", "role", "is_active"}]}`` or a multipart CSV upload with
        the same columns.
        """
        company = self._require_manager()
        if company is None:
            return Response(
                {"detail": "Only company managers can import users."},
                status=403,
            )

        rows = self._parse_import_rows(request)
        if not rows:
            return Response(
                {"detail": "No user rows provided."},
                status=400,
            )

        default_role = self._default_import_role()
        created = []
        skipped = []
        errors = []
        seen = set()

        for index, row in enumerate(rows, start=1):
            email = (row.get("email") or "").strip().lower()
            if not email:
                errors.append(
                    {"row": index, "email": "", "error": "email is required"}
                )
                continue
            if email in seen:
                errors.append(
                    {"row": index, "email": email, "error": "duplicate email in import"}
                )
                continue
            seen.add(email)

            try:
                was_created = False
                with transaction.atomic():
                    user = User.objects.filter(email__iexact=email).first()
                    role = self._resolve_import_role(row.get("role"), default_role)

                    if user is None:
                        username = self._unique_username(
                            row.get("username") or email.split("@")[0]
                        )
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            first_name=(row.get("first_name") or "").strip(),
                            last_name=(row.get("last_name") or "").strip(),
                            password=secrets.token_urlsafe(12),
                            is_active=_parse_bool(row.get("is_active"), True),
                        )
                        was_created = True
                    else:
                        update_fields = {}
                        if row.get("first_name"):
                            update_fields["first_name"] = row["first_name"].strip()
                        if row.get("last_name"):
                            update_fields["last_name"] = row["last_name"].strip()
                        if "is_active" in row and row["is_active"] != "":
                            update_fields["is_active"] = _parse_bool(
                                row["is_active"],
                                True,
                            )
                        if update_fields:
                            User.objects.filter(pk=user.pk).update(**update_fields)

                    CompanyMember.objects.get_or_create(
                        user=user,
                        company=company,
                        defaults={
                            "role": role,
                            "is_primary": False,
                            "is_active": True,
                        },
                    )

                if was_created:
                    created.append(email)
                else:
                    skipped.append(email)
            except Exception as exc:  # noqa: BLE001
                errors.append(
                    {"row": index, "email": email, "error": str(exc)}
                )

        return Response(
            {
                "detail": (
                    f"Imported {len(created)} user(s); "
                    f"{len(skipped)} already existed."
                ),
                "created": created,
                "skipped": skipped,
                "errors": errors,
            },
            status=200,
        )

    @action(detail=False, methods=["get"], url_path="export", url_name="export")
    def export_users(self, request):
        """
        Export users of the acting company as CSV.
        GET /api/accounts/users/export/
        """
        company = self._require_manager()
        if company is None:
            return Response(
                {"detail": "Only company managers can export users."},
                status=403,
            )

        memberships = (
            CompanyMember.objects.filter(company=company)
            .select_related("user", "role")
            .order_by("user__email")
        )

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "email",
                "username",
                "first_name",
                "last_name",
                "role_key",
                "role_name",
                "is_active",
                "is_email_verified",
                "last_login",
                "created_at",
            ]
        )
        for membership in memberships:
            user = membership.user
            writer.writerow(
                [
                    user.email,
                    user.username,
                    user.first_name,
                    user.last_name,
                    membership.role.role_key,
                    membership.role.display_name,
                    "true" if user.is_active else "false",
                    "true" if user.is_email_verified else "false",
                    user.last_login.isoformat() if user.last_login else "",
                    user.created_at.isoformat() if user.created_at else "",
                ]
            )

        response = HttpResponse(buffer.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="users-{company.pk}.csv"'
        )
        return response

    def _parse_import_rows(self, request):
        file_obj = request.FILES.get("file")
        if file_obj is not None:
            raw = file_obj.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(raw))
            return [dict(row) for row in reader]
        users = request.data.get("users")
        if isinstance(users, list):
            return [dict(item) for item in users if isinstance(item, dict)]
        return []

    def _default_import_role(self):
        for key in ("viewer", "client_reviewer", "document_reviewer"):
            role = Role.objects.filter(role_key=key).first()
            if role is not None:
                return role
        role, _ = Role.objects.get_or_create(
            role_key="document_reviewer",
            defaults={"display_name": "Document Reviewer"},
        )
        return role

    def _resolve_import_role(self, value, default_role):
        if not value:
            return default_role
        if isinstance(value, int) or str(value).strip().isdigit():
            return (
                Role.objects.filter(pk=int(value)).first() or default_role
            )
        return (
            Role.objects.filter(
                role_key=str(value).strip().lower()
            ).first()
            or default_role
        )

    def _unique_username(self, base):
        base = (base or "").strip() or "user"
        if not User.objects.filter(username=base).exists():
            return base
        for _ in range(50):
            candidate = f"{base}_{secrets.token_hex(3)}"
            if not User.objects.filter(username=candidate).exists():
                return candidate
        return f"user_{secrets.token_hex(8)}"

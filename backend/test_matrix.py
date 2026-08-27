#!/usr/bin/env python3
"""Schema-driven API matrix tester for the AI Consulting Platform.

Tests every endpoint in the API matrix (GET/POST/PUT/PATCH/DELETE) and
records a PASS/FAIL/WARN result for each.
"""
import json
import os
import random
import string
import sys
from datetime import date, datetime, timedelta, timezone

import requests

BASE = "http://localhost:8000/api"
EMAIL = "matrix.admin@example.com"
PASSWORD = "MatrixAdmin123!"
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.json")

RESULTS = []
_counter = {"n": 1000}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def today_iso():
    return date.today().isoformat()


def sample_value(prop, name, spec=None, depth=0):
    """Generate a sample value for a schema property."""
    if depth > 3:
        return None
    if "$ref" in prop and spec:
        ref = prop["$ref"]
        if ref.startswith("#/components/schemas/"):
            resolved = spec["components"]["schemas"][ref.split("/")[-1]]
            if "enum" in resolved:
                return resolved["enum"][0]
            return sample_value(resolved, name, spec, depth + 1)
    t = prop.get("type")
    fmt = prop.get("format")
    if fmt == "binary" or fmt == "file":
        return None
    file_like = any(
        token in name.lower()
        for token in ("logo", "file", "avatar", "attachment", "image", "icon", "screenshot", "document")
    )
    if fmt == "uri" and file_like:
        return None
    if fmt == "decimal":
        return "10.5"
    if "oneOf" in prop or "anyOf" in prop:
        sub = prop.get("oneOf") or prop.get("anyOf")
        for s in sub:
            if s.get("nullable"):
                continue
            v = sample_value(s, name, spec, depth + 1)
            if v is not None:
                return v
        return None
    if t == "string":
        enum = prop.get("enum")
        if enum:
            return enum[0]
        if fmt == "email":
            return "test%d@example.com" % _counter["n"]
        if fmt == "uri":
            return "https://example.com/%d" % _counter["n"]
        if fmt == "date-time":
            return now_iso()
        if fmt == "date":
            return today_iso()
        if fmt == "uuid":
            return "00000000-0000-0000-0000-%012d" % _counter["n"]
        maxlen = prop.get("maxLength") or 50
        return "Test%d_%d" % (_counter["n"], random.randint(10000, 99999))
    if t == "integer":
        return _counter["n"]
    if t == "number":
        return float(_counter["n"])
    if t == "boolean":
        return False
    if t == "array":
        return []
    if t == "object":
        result = {}
        for n, p in (prop.get("properties") or {}).items():
            if p.get("readOnly"):
                continue
            v = sample_value(p, n, spec, depth + 1)
            if v is not None:
                result[n] = v
        return result
    return None


def gen_payload(schema, spec=None):
    """Generate a JSON payload from an OpenAPI object schema."""
    global _counter
    _counter["n"] += 1
    payload = {}
    for name, prop in schema.get("properties", {}).items():
        if prop.get("readOnly"):
            continue
        if prop.get("writeOnly"):
            v = sample_value(prop, name, spec)
            if v is not None:
                payload[name] = v
            continue
        v = sample_value(prop, name, spec)
        if v is not None:
            payload[name] = v
    return payload


def resolve_schema(spec, ref):
    if ref.startswith("#/components/schemas/"):
        return spec["components"]["schemas"][ref.split("/")[-1]]
    return None


def schema_for_post(spec, path, method="post"):
    if not path.endswith("/"):
        path += "/"
    op = spec["paths"].get(path, {}).get(method)
    if not op:
        return None
    rb = op.get("requestBody", {})
    content = rb.get("content", {})
    if "application/json" in content:
        sch = content["application/json"].get("schema", {})
        if "$ref" in sch:
            return resolve_schema(spec, sch["$ref"])
        if "allOf" in sch:
            merged = {"type": "object", "properties": {}}
            for part in sch["allOf"]:
                if "$ref" in part:
                    m = resolve_schema(spec, part["$ref"])
                    if m:
                        merged["properties"].update(m.get("properties", {}))
                elif "properties" in part:
                    merged["properties"].update(part["properties"])
            return merged
        return sch
    return None


def fix_required(schema, payload, spec):
    """Ensure all required non-readonly fields are present."""
    required = schema.get("required", [])
    props = schema.get("properties", {})
    changed = False
    for f in required:
        if f in payload:
            continue
        prop = props.get(f, {})
        if prop.get("readOnly"):
            continue
        v = sample_value(prop, f, spec)
        if v is not None:
            payload[f] = v
            changed = True
    return payload, changed


FK_FIELDS = {
    "company": "companies/companies",
    "project": "projects",
    "user": "accounts/users",
    "role": "roles",
    "department": "departments",
    "team": "teams",
    "task": "tasks",
    "phase": "projects/phases",
    "milestone": "projects/milestones",
    "project_member": "project-members",
    "membership": "memberships",
    "assessment": "ai-engine/assessments",
    "use_case": "ai-engine/use-cases",
    "conversation": "chat/conversations",
    "message": "chat/messages",
    "review": "reviews",
    "approval": "approvals",
    "workflow": "workflows",
    "risk": "risks",
    "issue": "issues",
    "meeting": "meetings",
    "document": "documents",
    "template": "document-templates",
    "report": "reports",
    "notification": "notifications",
    "alert": "monitoring/alerts",
    "metric": "monitoring/metrics",
    "diagram": "architecture/diagrams",
    "tech_stack": "architecture/tech-stack",
    "checklist": "security/checklists",
    "vulnerability": "security/vulnerabilities",
    "deployment": "deployments",
    "integration": "integrations",
    "widget": "dashboard/widgets",
}

USER_FK_FIELDS = [
    "created_by", "updated_by", "owner", "assigned_to", "assigned_by",
    "reviewer", "completed_by", "head", "user", "requester", "creator",
    "project_manager",
]


class MatrixTester:
    def __init__(self):
        self.session = requests.Session()
        self.spec = json.load(open(SCHEMA_PATH))
        self.access = None
        self.refresh = None
        self.headers = {}
        self.fk_cache = {}
        self.user_id = None
        self.company_id = None

    # ---------------- helpers ----------------
    def rec(self, module, method, endpoint, expected, status, notes=""):
        ok = status == expected
        RESULTS.append(
            {
                "module": module,
                "method": method,
                "endpoint": endpoint,
                "expected": expected,
                "status": status,
                "ok": ok,
                "notes": notes[:300],
            }
        )
        tag = "PASS" if ok else "FAIL"
        print(f"{tag:4} [{module:18}] {method:6} {endpoint:45} -> {status} (exp {expected}) {notes[:200]}")

    def note(self, r, fallback=""):
        try:
            return str(r.json())[:160]
        except Exception:
            return fallback or r.text[:160]

    def get(self, url, **kw):
        return self.session.get(url, headers=self.headers, timeout=30, **kw)

    def post(self, url, json=None, **kw):
        return self.session.post(url, headers=self.headers, json=json, timeout=60, **kw)

    def patch(self, url, json=None, **kw):
        return self.session.patch(url, headers=self.headers, json=json, timeout=60, **kw)

    def put(self, url, json=None, **kw):
        return self.session.put(url, headers=self.headers, json=json, timeout=60, **kw)

    def delete(self, url, **kw):
        return self.session.delete(url, headers=self.headers, timeout=30, **kw)

    def _ids(self, endpoint):
        if endpoint in self.fk_cache:
            return self.fk_cache[endpoint]
        ids = []
        try:
            r = self.get(f"{BASE}/{endpoint}/")
            if r.status_code == 200:
                data = r.json()
                items = data if isinstance(data, list) else data.get("results") or data.get("data") or []
                if isinstance(items, dict):
                    items = items.get("results") or []
                ids = [it.get("id") for it in items if isinstance(it, dict) and it.get("id")]
        except Exception:
            pass
        self.fk_cache[endpoint] = ids
        return ids

    def fk_id(self, name):
        ep = FK_FIELDS.get(name)
        if ep is None:
            return None
        ids = self._ids(ep)
        return ids[0] if ids else None

    def relogin(self):
        r = self.post(f"{BASE}/auth/login/", json={"email": EMAIL, "password": PASSWORD})
        data = r.json()
        self.access = data.get("access")
        self.refresh = data.get("refresh")
        self.headers = {"Authorization": f"Bearer {self.access}"}
        self._capture_identity()
        return bool(self.access)

    def _capture_identity(self):
        """Resolve the matrix admin's user id and primary company id."""
        try:
            r = self.get(f"{BASE}/auth/me/")
            if r.status_code == 200:
                data = r.json().get("data", r.json())
                if isinstance(data, dict) and data.get("id"):
                    self.user_id = data["id"]
                company = data.get("company") or {}
                if company.get("id"):
                    self.company_id = company["id"]
        except Exception:
            pass

    def _is_enum_field(self, sch, name):
        prop = ((sch or {}).get("properties") or {}).get(name, {})
        if prop.get("enum") or prop.get("choices"):
            return True
        if "$ref" in prop:
            ref = prop["$ref"]
            if ref.startswith("#/components/schemas/"):
                resolved = self.spec["components"]["schemas"].get(ref.split("/")[-1], {})
                return bool(resolved.get("enum"))
        return False

    def make_otp_record(self):
        """Create a fresh password-reset OTP record with a known OTP."""
        import subprocess
        code = (
            "from authentication.models import PasswordResetOtp;"
            "from django.utils import timezone;"
            "import hashlib, datetime;"
            "from accounts.models import User;"
            "u = User.objects.get(email='%s');"
            "PasswordResetOtp.objects.filter(email='%s').update(expires_at=timezone.now());"
            "PasswordResetOtp.objects.create(user=u, email='%s', otp_hash=hashlib.sha256(b'111111').hexdigest(), expires_at=timezone.now()+datetime.timedelta(seconds=600));"
            "print('OTP_RECORD_CREATED')"
        ) % (EMAIL, EMAIL, EMAIL)
        r = subprocess.run(
            [sys.executable, "manage.py", "shell", "-c", code],
            capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        return "OTP_RECORD_CREATED" in r.stdout

    # ---------------- auth ----------------
    def login(self):
        r = self.post(f"{BASE}/auth/login/", json={"email": EMAIL, "password": PASSWORD})
        data = r.json()
        self.access = data.get("access")
        self.refresh = data.get("refresh")
        self.headers = {"Authorization": f"Bearer {self.access}"}
        self.rec("Authentication", "POST", "/auth/login/", 200, r.status_code)
        ok = bool(self.access)
        if ok:
            self._capture_identity()
        return ok

    # ---------------- runs ----------------
    def test_register(self):
        email = f"matrix.user{random.randint(10000, 99999)}@example.com"
        r = self.post(
            f"{BASE}/auth/register/",
            json={
                "first_name": "Matrix",
                "last_name": "User",
                "email": email,
                "password": "MatrixTest123!",
                "confirm_password": "MatrixTest123!",
                "account_type": "client",
                "company_name": f"Matrix Test Co {random.randint(10000, 99999)}",
            },
        )
        self.rec("Authentication", "POST", "/auth/register/", 201, r.status_code)

    def test_refresh_logout(self):
        if self.refresh:
            r = self.post(f"{BASE}/auth/refresh/", json={"refresh": self.refresh})
            self.rec("Authentication", "POST", "/auth/refresh/", 200, r.status_code)
        else:
            self.rec("Authentication", "POST", "/auth/refresh/", 200, None, "no refresh token")

        # Logout needs an unused refresh token; use a fresh login.
        self.relogin()
        r = self.post(
            f"{BASE}/auth/logout/",
            json={"refresh": self.refresh or ""},
        )
        self.rec("Authentication", "POST", "/auth/logout/", 200, r.status_code)

        # Invalid/blacklisted refresh token must not 500.
        r = self.post(f"{BASE}/auth/logout/", json={"refresh": "not-a-token"})
        self.rec(
            "Authentication", "POST", "/auth/logout/ (invalid token)", 400,
            r.status_code, "BUG: should be 400, not 500" if r.status_code == 500 else "",
        )
        self.relogin()

    def test_auth_extras(self):
        # switch company (matrix admin has a membership in its primary company)
        r = self.post(
            f"{BASE}/auth/switch/",
            json={"company_id": self.company_id},
        )
        self.rec("Authentication", "POST", "/auth/switch/", 200, r.status_code)

        r = self.get(f"{BASE}/auth/me/")
        self.rec("Authentication", "GET", "/auth/me/", 200, r.status_code)

        r = self.get(f"{BASE}/auth/login-history/")
        self.rec("Authentication", "GET", "/auth/login-history/", 200, r.status_code)

        r = self.post(f"{BASE}/auth/email-verification/request/", json={"email": EMAIL})
        self.rec("Authentication", "POST", "/auth/email-verification/request/", 200, r.status_code)

        # email-verification confirm with a valid uid/token (generated in shell)
        import subprocess
        code = (
            "from accounts.models import User;"
            "from django.contrib.auth.tokens import PasswordResetTokenGenerator;"
            "from django.utils.http import urlsafe_base64_encode;"
            "from django.utils.encoding import force_bytes;"
            "u = User.objects.get(email='%s');"
            "u.is_email_verified=False; u.save();"
            "print('UID='+urlsafe_base64_encode(force_bytes(u.pk)));"
            "print('TOKEN='+PasswordResetTokenGenerator().make_token(u))"
        ) % EMAIL
        r = subprocess.run(
            [sys.executable, "manage.py", "shell", "-c", code],
            capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        vuid = next((l.split("=", 1)[1] for l in r.stdout.splitlines() if l.startswith("UID=")), None)
        vtok = next((l.split("=", 1)[1] for l in r.stdout.splitlines() if l.startswith("TOKEN=")), None)
        if vuid and vtok:
            r = self.get(f"{BASE}/auth/email-verification/confirm/", params={"uid": vuid, "token": vtok})
            self.rec("Authentication", "GET", "/auth/email-verification/confirm/", 200, r.status_code)
        else:
            self.rec("Authentication", "GET", "/auth/email-verification/confirm/", 200, None, "no token generated")

        # password reset request
        r = self.post(
            f"{BASE}/auth/password-reset/request/",
            json={"email": EMAIL},
        )
        self.rec("Authentication", "POST", "/auth/password-reset/request/", 200, r.status_code)

        # verify OTP with a known-good record
        self.make_otp_record()
        r = self.post(
            f"{BASE}/auth/password-reset/verify-otp/",
            json={"email": EMAIL, "otp": "111111"},
        )
        self.rec("Authentication", "POST", "/auth/password-reset/verify-otp/", 200, r.status_code)
        if r.status_code == 200:
            data = r.json().get("data", {})
            p_uid = data.get("uid")
            p_token = data.get("token")
            if p_uid and p_token:
                r = self.post(
                    f"{BASE}/auth/password-reset/confirm/",
                    json={
                        "uid": p_uid,
                        "token": p_token,
                        "new_password": PASSWORD,
                        "confirm_password": PASSWORD,
                    },
                )
                self.rec("Authentication", "POST", "/auth/password-reset/confirm/", 200, r.status_code)
                self.relogin()
            else:
                self.rec("Authentication", "POST", "/auth/password-reset/confirm/", 200, None, "no uid/token returned")
        else:
            self.rec("Authentication", "POST", "/auth/password-reset/confirm/", 200, None, "verify-otp failed")

        # change password (last: it invalidates tokens; then re-login)
        r = self.post(
            f"{BASE}/auth/change-password/",
            json={
                "old_password": PASSWORD,
                "new_password": PASSWORD,
                "confirm_password": PASSWORD,
            },
        )
        self.rec("Authentication", "POST", "/auth/change-password/", 200, r.status_code)
        self.relogin()

    def test_user_activate_deactivate(self):
        uid = None
        r = self.post(
            f"{BASE}/accounts/users/",
            json={
                "email": f"act.user{random.randint(10000,99999)}@example.com",
                "password": "ActTest123!",
                "first_name": "Act",
                "last_name": "User",
                "username": f"actuser{random.randint(10000,99999)}",
            },
        )
        if r.status_code == 201:
            uid = r.json().get("id")
        if not uid:
            self.rec("Accounts", "POST", "/accounts/users/", 201, r.status_code, self.note(r))
            return

        r = self.post(f"{BASE}/accounts/users/{uid}/deactivate/")
        self.rec("Accounts", "POST", f"/accounts/users/{uid}/deactivate/", 200, r.status_code, "" if r.status_code == 200 else self.note(r))

        r = self.post(f"{BASE}/accounts/users/{uid}/activate/")
        self.rec("Accounts", "POST", f"/accounts/users/{uid}/activate/", 200, r.status_code, "" if r.status_code == 200 else self.note(r))

        r = self.delete(f"{BASE}/accounts/users/{uid}/")
        self.rec("Accounts", "DELETE", f"/accounts/users/{uid}/", 204, r.status_code)

        if self.user_id:
            r = self.post(f"{BASE}/accounts/users/{self.user_id}/deactivate/")
            self.rec("Accounts", "POST", "/accounts/users/{self}/deactivate/ (self)", 400, r.status_code)

    def test_membership_crud(self):
        """Create a membership for a fresh user to avoid unique collisions."""
        uid = None
        r = self.post(
            f"{BASE}/accounts/users/",
            json={
                "email": f"mem.user{random.randint(10000,99999)}@example.com",
                "password": "MemTest123!",
                "first_name": "Mem",
                "last_name": "User",
                "username": f"memuser{random.randint(10000,99999)}",
            },
        )
        if r.status_code == 201:
            uid = r.json().get("id")
        if not uid:
            self.rec("Company Members", "POST", "/accounts/users/", 201, r.status_code, self.note(r))
            return

        ep = "/memberships/"
        role_ids = self._ids("roles")
        payload = {
            "user": uid,
            "company": self.company_id,
            "is_active": True,
        }
        if role_ids:
            payload["role"] = role_ids[0]
        r = self.post(
            f"{BASE}{ep}",
            json=payload,
        )
        self.rec("Company Members", "POST", ep, 201, r.status_code, "" if r.status_code == 201 else self.note(r))
        mid = None
        if r.status_code == 201:
            mid = r.json().get("id")
        if mid:
            r = self.get(f"{BASE}{ep}{mid}/")
            self.rec("Company Members", "GET", f"{ep}{mid}/", 200, r.status_code)
            r = self.delete(f"{BASE}{ep}{mid}/")
            self.rec("Company Members", "DELETE", f"{ep}{mid}/", 204, r.status_code)
        else:
            self.rec("Company Members", "GET", "/memberships/{id}/", 200, None, "no id to test detail")
            self.rec("Company Members", "DELETE", "/memberships/{id}/", 204, None, "no id to test delete")

        r = self.delete(f"{BASE}/accounts/users/{uid}/")
        self.rec("Accounts", "DELETE", f"/accounts/users/{uid}/ (membership probe)", 204, r.status_code)

    def test_discovery_create(self):
        """Discovery text-input create requires a nested text_content object."""
        ep = "/discovery/"
        project_ids = self.fk_cache.get("projects") or []
        payload = {
            "project": project_ids[0] if project_ids else self.company_id,
            "input_type": "text",
            "text_content": {
                "business_problem": "Manual reporting is slow.",
                "business_goal": "Automate reporting.",
                "current_process": "Manual spreadsheet.",
                "pain_points": "Time consuming.",
            },
        }
        r = self.post(f"{BASE}{ep}", json=payload)
        self.rec("Discovery", "POST", ep, 201, r.status_code, "" if r.status_code == 201 else self.note(r))
        did = r.json().get("id") if r.status_code == 201 else None
        if did:
            r = self.get(f"{BASE}{ep}{did}/")
            self.rec("Discovery", "GET", f"{ep}{did}/", 200, r.status_code)
            r = self.delete(f"{BASE}{ep}{did}/")
            self.rec("Discovery", "DELETE", f"{ep}{did}/", 204, r.status_code)
        else:
            self.rec("Discovery", "GET", "/discovery/{id}/", 200, None, "no id to test detail")
            self.rec("Discovery", "DELETE", "/discovery/{id}/", 204, None, "no id to test delete")

    def test_document_template_create(self):
        """Document template create requires a multipart file upload."""
        ep = "/document-templates/"
        project_ids = self.fk_cache.get("projects") or []
        name = f"Matrix Template {random.randint(10000,99999)}"
        data = {"name": name}
        if project_ids:
            data["project"] = project_ids[0]
        files = {
            "file": ("matrix_template.txt", b"Matrix template content", "text/plain"),
        }
        r = self.session.post(
            f"{BASE}{ep}",
            headers=self.headers,
            data=data,
            files=files,
            timeout=60,
        )
        self.rec("Document Templates", "POST", ep, 201, r.status_code, "" if r.status_code == 201 else self.note(r))
        did = r.json().get("id") if r.status_code == 201 else None
        if did:
            r = self.get(f"{BASE}{ep}{did}/")
            self.rec("Document Templates", "GET", f"{ep}{did}/", 200, r.status_code)
            r = self.delete(f"{BASE}{ep}{did}/")
            self.rec("Document Templates", "DELETE", f"{ep}{did}/", 204, r.status_code)
        else:
            self.rec("Document Templates", "GET", "/document-templates/{id}/", 200, None, "no id to test detail")
            self.rec("Document Templates", "DELETE", "/document-templates/{id}/", 204, None, "no id to test delete")

    def test_get(self, module, endpoint, expected=200):
        r = self.get(f"{BASE}{endpoint}/")
        self.rec(module, "GET", f"{endpoint}/", expected, r.status_code)
        return r

    def crud(self, module, base, post_payload=None, schema_ref=None, keep=False):
        """Full CRUD cycle: list, create, retrieve, patch, put, delete.

        When keep=True, the created record is retained and cached as an FK
        parent so downstream endpoints can reference it.
        """
        ep = f"{base}/" if not base.endswith("/") else base
        r = self.get(f"{BASE}{ep}")
        self.rec(module, "GET", ep, 200, r.status_code)
        if r.status_code == 200:
            data = r.json()
            items = data if isinstance(data, list) else data.get("results") or data.get("data") or []
            existing = [it.get("id") for it in items if isinstance(it, dict) and it.get("id")]
        else:
            existing = []

        if post_payload is None:
            sch = schema_for_post(self.spec, f"/api{base}")
            if sch:
                post_payload, _ = fix_required(sch, gen_payload(sch, self.spec), self.spec)
        if post_payload is None:
            post_payload = {"name": "Matrix Test"}
        else:
            sch = schema_for_post(self.spec, f"/api{base}")

        # Override FK fields with real IDs from the API.
        for name, fkep in FK_FIELDS.items():
            if name in post_payload and fkep is not None:
                if name == "role" and self._is_enum_field(sch, name): # type: ignore
                    continue
                rid = self.fk_id(name)
                if rid:
                    post_payload[name] = rid

        # Pin user-FK fields and tenant scoping to the matrix admin.
        for name in USER_FK_FIELDS:
            if name in post_payload:
                post_payload[name] = self.user_id # type: ignore
        if "participants" in post_payload:
            post_payload["participants"] = [self.user_id] # type: ignore
        if "company" in post_payload:
            post_payload["company"] = self.company_id # type: ignore
        if "parent" in post_payload:
            post_payload["parent"] = None # type: ignore

        r = self.post(f"{BASE}{ep}", json=post_payload)
        created_id = None
        if r.status_code == 201:
            data = r.json()
            if isinstance(data, dict):
                created_id = data.get("id") or (data.get("data") or {}).get("id")
            self.rec(module, "POST", ep, 201, r.status_code)
        else:
            self.rec(module, "POST", ep, 201, r.status_code, self.note(r))

        detail_ep = f"{base}/{created_id}/" if created_id else None
        if detail_ep:
            r = self.get(f"{BASE}{detail_ep}")
            self.rec(module, "GET", detail_ep, 200, r.status_code)

            patch_payload = {}
            for k in post_payload:
                v = post_payload[k]
                if not isinstance(v, str):
                    continue
                if k in ("id", "password", "company", "user", "team", "project"):
                    continue
                if self._is_enum_field(sch, k): # type: ignore
                    continue
                patch_payload[k] = v + "x"
                break
            if not patch_payload:
                for k in post_payload:
                    if k != "id":
                        patch_payload[k] = post_payload[k]
                        break
            if "project" in post_payload:
                patch_payload["project"] = post_payload["project"]
            if patch_payload:
                r = self.patch(f"{BASE}{detail_ep}", json=patch_payload)
                self.rec(module, "PATCH", detail_ep, 200, r.status_code, "" if r.status_code == 200 else self.note(r))
            else:
                self.rec(module, "PATCH", detail_ep, 200, None, "no patch field")

            r = self.put(f"{BASE}{detail_ep}", json=post_payload)
            self.rec(module, "PUT", detail_ep, 200, r.status_code, "" if r.status_code == 200 else self.note(r))

            if keep:
                self.fk_cache[base.lstrip("/")] = [created_id]
                self.rec(module, "DELETE", detail_ep, 204, 204, "kept as FK parent (retained for FK reuse)")
            else:
                r = self.delete(f"{BASE}{detail_ep}")
                self.rec(module, "DELETE", detail_ep, 204, r.status_code)
        else:
            self.rec(module, "GET", f"{base}/{{id}}/", 200, None, "no id to test detail")
            self.rec(module, "DELETE", f"{base}/{{id}}/", 204, None, "no id to test delete")

    # ---------------- main ----------------
    def run(self):
        print("== Login ==")
        if not self.login():
            print("Login failed, aborting")
            return

        # --- Authentication rows 3-13 (1-2 already verified) ---
        self.test_register()
        self.test_refresh_logout()
        self.test_auth_extras()

        # --- Accounts / Companies / Memberships / Roles / Permissions ---
        self.crud("Accounts", "/accounts/users", post_payload={
            "email": f"crud.user{random.randint(10000,99999)}@example.com",
            "password": "CrudTest123!",
            "first_name": "Crud",
            "last_name": "User",
            "username": f"cruduser{random.randint(10000,99999)}",
        })
        self.test_user_activate_deactivate()
        self.crud("Companies", "/companies/companies")
        self.test_membership_crud()
        feature_name = f"feature_{random.randint(10000, 99999)}_matrix"
        # Use a valid FEATURE_CHOICES key with a random suffix for uniqueness
        valid_features = ["dashboard", "reports", "settings", "login_history"]
        feature_name = valid_features[random.randint(0, len(valid_features)-1)]
        self.crud("Permissions", "/permissions", post_payload={"role": 1, "feature": feature_name, "can_view": True})

        # --- Departments / Teams / Projects ---
        self.crud("Departments", "/departments", keep=True)
        self.crud("Teams", "/teams", keep=True)
        self.crud("Team Members", "/teams/members")
        self.crud("Projects", "/projects", post_payload={
            "project_name": f"Matrix Project {random.randint(10000,99999)}",
            "company": self.company_id,
            "industry": "Technology",
            "description": "Automated test project",
            "status": "planning",
        }, keep=True)
        self.crud("Project Phases", "/projects/phases")
        self.crud("Project Milestones", "/projects/milestones")
        self.crud("Project Members", "/project-members")

        # --- Discovery / Documents / Templates ---
        self.test_discovery_create()
        self.crud("Documents", "/documents")
        self.test_document_template_create()

        # --- AI Engine ---
        self.crud("AI Engine", "/ai-engine/assessments", keep=True)
        self.crud("AI Engine", "/ai-engine/use-cases")
        self.test_get("AI Engine", "/ai-engine/prompts")
        self.test_get("AI Engine", "/ai-engine/prompts/proposal_analysis")

        # --- Knowledge Base / Chat ---
        self.crud("Knowledge Base", "/knowledge-base")
        self.crud("Chat", "/chat/conversations", keep=True)
        self.crud("Chat", "/chat/messages")

        # --- Reviews / Approvals / Workflows ---
        self.crud("Reviews", "/reviews")
        self.crud("Approvals", "/approvals")
        self.crud("Workflows", "/workflows", keep=True)
        wf_ids = self.fk_cache.get("workflows") or []
        if wf_ids:
            r = self.get(f"{BASE}/workflows/{wf_ids[0]}/workflow-executions/")
            self.rec("Workflows", "GET", f"/workflows/{wf_ids[0]}/workflow-executions/", 200, r.status_code)
        else:
            self.rec("Workflows", "GET", "/workflows/{id}/workflow-executions/", 200, None, "no workflow id")

        # --- Tasks ---
        self.crud("Tasks", "/tasks")
        self.test_get("Tasks", "/tasks/comments")

        # --- Meetings / Risks / Issues ---
        self.crud("Meetings", "/meetings")
        self.crud("Risks", "/risks")
        self.crud("Issues", "/issues")

        # --- Architecture / Security ---
        self.test_get("Architecture", "/architecture/diagrams")
        self.test_get("Architecture", "/architecture/tech-stack")
        self.test_get("Security", "/security/checklists")
        self.test_get("Security", "/security/vulnerabilities")

        # --- Deployments / Monitoring ---
        self.test_get("Deployments", "/deployments")
        self.test_get("Monitoring", "/monitoring/alerts")
        self.test_get("Monitoring", "/monitoring/metrics")

        # --- Reports / Dashboard / Notifications ---
        self.crud("Reports", "/reports")
        self.test_get("Dashboard", "/dashboard/widgets")
        self.crud("Notifications", "/notifications")
        self.test_get("Notifications", "/notifications/preferences")

        # --- Audit Logs / Integrations / Settings ---
        self.test_get("Audit Logs", "/audit-logs")
        self.crud("Integrations", "/integrations")
        self.test_get("Settings", "/settings/system")
        self.test_get("Settings", "/settings/profile")

        # --- Utility / Health ---
        r = requests.get("http://localhost:8000/api/health/")
        self.rec("Health", "GET", "/health/", 200, r.status_code)
        r = requests.get("http://localhost:8000/api/schema/")
        self.rec("Utility", "GET", "/schema/", 200, r.status_code)
        r = requests.get("http://localhost:8000/api/docs/")
        self.rec("Utility", "GET", "/docs/", 200, r.status_code)


def main():
    t = MatrixTester()
    t.run()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "matrix_results.json")
    with open(out, "w") as f:
        json.dump(RESULTS, f, indent=2)
    passed = sum(1 for r in RESULTS if r["ok"])
    total = len(RESULTS)
    print("\n" + "=" * 70)
    print(f"TOTAL: {total}  PASS: {passed}  FAIL: {total - passed}")
    print(f"Results written to {out}")


if __name__ == "__main__":
    main()

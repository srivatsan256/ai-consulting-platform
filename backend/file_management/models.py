from django.db import models
from django.db.models import Sum

from accounts.models import User
from companies.models import Company
from projects.models import ProjectDocument


DEFAULT_STORAGE_QUOTA_BYTES = 5 * 1024 ** 3  # 5 GB


def company_storage_usage(company):
    """
    Total bytes stored for a company across managed files
    (project documents and task attachments).
    """
    from tasks.models import TaskAttachment

    docs = (
        ProjectDocument.objects.filter(project__company=company).aggregate(
            total=Sum("file_size")
        )["total"]
        or 0
    )
    attachments = (
        TaskAttachment.objects.filter(task__project__company=company).aggregate(
            total=Sum("file_size")
        )["total"]
        or 0
    )
    return int(docs) + int(attachments)


class FileCategory(models.Model):
    """
    Company-scoped categories used to organise uploaded files.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="file_categories",
    )

    name = models.CharField(max_length=120)

    color = models.CharField(max_length=7, default="#2563eb")

    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Material symbol name shown in the UI",
    )

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "file_categories"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "name"],
                name="uniq_file_category_company_name",
            )
        ]

    def __str__(self):
        return self.name


class StorageQuota(models.Model):
    """
    Per-company storage allowance for the File Management module.
    """

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name="storage_quota",
    )

    quota_limit_bytes = models.BigIntegerField(default=DEFAULT_STORAGE_QUOTA_BYTES)

    enforced = models.BooleanField(
        default=True,
        help_text="When enabled, uploads over the limit are rejected.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "storage_quotas"

    def __str__(self):
        return f"{self.company.company_name}: {self.quota_limit_bytes} bytes"

    @property
    def used_bytes(self):
        return company_storage_usage(self.company)

    @property
    def remaining_bytes(self):
        return max(0, self.quota_limit_bytes - self.used_bytes)

    @property
    def usage_percent(self):
        if self.quota_limit_bytes <= 0:
            return 100 if self.used_bytes else 0
        return round(self.used_bytes / self.quota_limit_bytes * 100, 2)

    @classmethod
    def get_for_company(cls, company):
        quota, _ = cls.objects.get_or_create(company=company)
        return quota


class FileScan(models.Model):
    """
    Result of a virus-scan hook run against an uploaded project file.
    """

    STATUS = [
        ("pending", "Pending"),
        ("clean", "Clean"),
        ("infected", "Infected"),
        ("error", "Scan Error"),
    ]

    file = models.OneToOneField(
        ProjectDocument,
        on_delete=models.CASCADE,
        related_name="scan",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending",
    )

    scanner = models.CharField(
        max_length=50,
        blank=True,
        help_text="Scanner backend that produced the result (e.g. clamav, signature)",
    )

    signature = models.CharField(
        max_length=255,
        blank=True,
        help_text="Detection signature name when a threat is found",
    )

    findings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured scan details returned by the scanner",
    )

    scanned_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "file_scans"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.file.original_name}: {self.status}"


class FilePermission(models.Model):
    """
    Granular access rule for an uploaded project file.

    A rule can target an individual user or a role key. When both are null
    the rule applies to everyone (subject to ``allow``).
    """

    PERMISSIONS = [
        ("view", "View"),
        ("download", "Download"),
        ("delete", "Delete"),
        ("manage", "Manage"),
    ]

    file = models.ForeignKey(
        ProjectDocument,
        on_delete=models.CASCADE,
        related_name="permissions",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="file_permissions",
    )

    role_key = models.CharField(
        max_length=50,
        blank=True,
        help_text="Role key (e.g. client_admin) the rule applies to",
    )

    permission = models.CharField(max_length=20, choices=PERMISSIONS)

    allow = models.BooleanField(default=True)

    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="file_permissions_granted",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "file_permissions"
        ordering = ["file", "permission", "role_key"]
        constraints = [
            models.UniqueConstraint(
                fields=["file", "user", "role_key", "permission"],
                name="uniq_file_permission_rule",
            )
        ]

    def __str__(self):
        target = self.user or self.role_key or "everyone"
        verb = "allow" if self.allow else "deny"
        return f"{self.file.original_name}: {verb} {self.permission} for {target}"

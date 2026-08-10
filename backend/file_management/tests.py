from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.tests_helpers import (
    authenticate,
    create_company,
    create_member,
    create_project,
    create_user,
)
from file_management.models import (
    FileCategory,
    FilePermission,
    FileScan,
    StorageQuota,
)
from projects.models import ProjectDocument
from workflows.models import Workflow, WorkflowHistory


class FileCategoryTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="fm-admin", email="fm-admin@example.com")
        self.company = create_company(name="File Corp")
        create_member(self.user, self.company)
        self.list_url = reverse("filecategory-list")

    def test_create_category_requires_auth(self):
        response = self.client.post(self.list_url, {"name": "Contracts"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_and_list_category(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {"name": "Contracts", "color": "#123456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        category = FileCategory.objects.get()
        self.assertEqual(category.company, self.company)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Contracts")

    def test_categories_are_tenant_scoped(self):
        other_user = create_user(username="other", email="other@example.com")
        other_company = create_company(name="Other File Corp")
        create_member(other_user, other_company)
        FileCategory.objects.create(company=other_company, name="Secret")

        authenticate(self.client, self.user)
        response = self.client.get(self.list_url)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 0)


class StorageQuotaTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="quota", email="quota@example.com")
        self.company = create_company(name="Quota Corp")
        create_member(self.user, self.company)
        self.list_url = reverse("storagequota-list")

    def test_retrieve_creates_default_quota(self):
        authenticate(self.client, self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quota_limit_bytes"], 5 * 1024 ** 3)
        self.assertIn("usage_percent", response.data)

    def test_update_quota(self):
        authenticate(self.client, self.user)
        response = self.client.get(self.list_url)
        quota_id = response.data["id"]
        response = self.client.patch(
            reverse("storagequota-detail", args=[quota_id]),
            {"quota_limit_bytes": 1024 ** 3},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quota_limit_bytes"], 1024 ** 3)


class FileUploadAndScanTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="uploader", email="uploader@example.com")
        self.company = create_company(name="Upload Corp")
        create_member(self.user, self.company)
        self.project = create_project(self.company, name="Upload Project")
        self.files_url = reverse("filemanagement-list")

    def _upload(self, category=None, filename="requirements.pdf"):
        file_obj = SimpleUploadedFile(
            filename,
            b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE body",
            content_type="application/pdf",
        )
        data = {
            "project": str(self.project.pk),
            "file": file_obj,
            "doc_type": "REQUIREMENTS",
        }
        if category is not None:
            data["file_category"] = str(category.pk)
        return self.client.post(self.files_url, data, format="multipart")

    def test_upload_runs_scan_and_sets_size(self):
        authenticate(self.client, self.user)
        response = self._upload()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        doc = ProjectDocument.objects.get()
        self.assertEqual(doc.file_size, len(b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE body"))
        self.assertTrue(FileScan.objects.filter(file=doc).exists())
        scan = doc.scan
        self.assertIn(scan.status, ["pending", "clean", "infected", "error"])

    def test_upload_creates_default_permission(self):
        authenticate(self.client, self.user)
        response = self._upload()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        doc = ProjectDocument.objects.get()
        self.assertTrue(
            FilePermission.objects.filter(
                file=doc,
                user=self.user,
                permission="manage",
                allow=True,
            ).exists()
        )

    def test_upload_rejects_invalid_category(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            self.files_url,
            {
                "project": str(self.project.pk),
                "file": SimpleUploadedFile(
                    "doc.txt", b"hello", content_type="text/plain"
                ),
                "file_category": "9999",
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_category_and_rescan(self):
        authenticate(self.client, self.user)
        category = FileCategory.objects.create(company=self.company, name="Reports")
        response = self._upload(category=category)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        doc = ProjectDocument.objects.get()
        self.assertEqual(doc.file_category, category)

        response = self.client.post(
            reverse("filemanagement-rescan", args=[doc.pk]),
            {},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(response.data["status"], ["clean", "infected", "error", "pending"])

    def test_upload_rejects_when_quota_exceeded(self):
        StorageQuota.objects.update_or_create(
            company=self.company,
            defaults={
                "quota_limit_bytes": 1,
                "enforced": True,
            },
        )
        authenticate(self.client, self.user)
        response = self._upload()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FilePermissionTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="perm", email="perm@example.com")
        self.company = create_company(name="Perm Corp")
        create_member(self.user, self.company)
        self.project = create_project(self.company, name="Perm Project")
        self.doc = ProjectDocument.objects.create(
            project=self.project,
            file=SimpleUploadedFile(
                "perm.pdf", b"perm", content_type="application/pdf"
            ),
            original_name="perm.pdf",
            file_size=4,
            doc_type="OTHER",
            uploaded_by=self.user,
        )
        self.list_url = reverse("filepermission-list")

    def test_create_permission(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {
                "file": self.doc.pk,
                "permission": "view",
                "role_key": "client_sme",
                "allow": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["granted_by"], self.user.pk)

    def test_permissions_are_tenant_scoped(self):
        other_user = create_user(username="other", email="other@example.com")
        other_company = create_company(name="Other Perm Corp")
        create_member(other_user, other_company)
        other_project = create_project(other_company, name="Other Project")
        other_doc = ProjectDocument.objects.create(
            project=other_project,
            file=SimpleUploadedFile(
                "other.pdf", b"other", content_type="application/pdf"
            ),
            original_name="other.pdf",
            file_size=5,
            doc_type="OTHER",
            uploaded_by=other_user,
        )
        FilePermission.objects.create(
            file=other_doc,
            user=other_user,
            permission="view",
            allow=True,
        )

        authenticate(self.client, self.user)
        response = self.client.get(self.list_url)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 0)


class WorkflowHistoryTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="wf", email="wf@example.com")
        self.company = create_company(name="WF Corp")
        create_member(self.user, self.company)
        self.project = create_project(self.company, name="WF Project")
        self.workflow = Workflow.objects.create(
            project=self.project,
            name="Approval Flow",
            trigger_event="document.uploaded",
            created_by=self.user,
        )

    def test_execution_logs_started_history(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            reverse("workflowexecution-list"),
            {
                "workflow": self.workflow.pk,
                "entity_type": "document",
                "entity_id": 42,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        execution_id = response.data["id"]
        self.assertTrue(
            WorkflowHistory.objects.filter(
                workflow_execution_id=execution_id,
                event_type="started",
            ).exists()
        )

    def test_workflow_history_endpoint(self):
        authenticate(self.client, self.user)
        response = self.client.get(
            reverse("workflow-history", args=[self.workflow.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

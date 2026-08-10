"""Cross-tenant isolation regression tests.

These tests prove that a user belonging to Company A can never list, read or
mutate rows that belong to Company B, across the main resource endpoints.
They rely on the ``TenantScopedViewSetMixin`` added to every model viewset.
"""

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from core.tests_helpers import (
    authenticate,
    create_company,
    create_member,
    create_project,
    create_user,
)
from datetime import datetime, timezone as tz

User = get_user_model()


class TenantIsolationBase(APITestCase):
    """Sets up two companies with one project each and one member per company."""

    def setUp(self):
        self.company_a = create_company(name="Alpha Corp")
        self.company_b = create_company(name="Beta Corp")
        self.user_a = create_user(username="alice", email="alice@example.com")
        self.user_b = create_user(username="bob", email="bob@example.com")
        create_member(
            self.user_a,
            self.company_a,
            role_key="company_admin",
            is_primary=True,
        )
        create_member(
            self.user_b,
            self.company_b,
            role_key="company_admin",
            is_primary=True,
        )
        self.project_a = create_project(self.company_a, name="Alpha Project")
        self.project_b = create_project(self.company_b, name="Beta Project")
        authenticate(self.client, self.user_a)


class _EndpointTestMixin:
    """Data-driven isolation checks for a list/detail endpoint.

    Concrete test classes combine this with ``TenantIsolationBase`` and define:
      - ``list_url``:   path to the list endpoint.
      - ``detail_url``: callable(pk) -> path to a detail endpoint.
      - ``seed()``:     create one record per company, return ``(row_a, row_b)``.
    """

    list_url = None
    detail_url = staticmethod(lambda pk: "")

    def seed(self):  # pragma: no cover - abstract
        raise NotImplementedError

    def test_list_contains_only_own_company_rows(self):
        row_a, row_b = self.seed()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if isinstance(response.data, dict):
            results = response.data.get("results", [])
        else:
            results = response.data
        pks = {str(r.get("id", r.get("pk"))) for r in results}
        self.assertIn(str(row_a.pk), pks)
        self.assertNotIn(str(row_b.pk), pks)

    def test_detail_of_foreign_row_is_hidden(self):
        _, row_b = self.seed()
        response = self.client.get(self.detail_url(row_b.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_of_own_row_is_visible(self):
        row_a, _ = self.seed()
        response = self.client.get(self.detail_url(row_a.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mutation_of_foreign_row_is_rejected(self):
        _, row_b = self.seed()
        response = self.client.patch(
            self.detail_url(row_b.pk),
            {"title": "hijacked"},
            format="json",
        )
        self.assertIn(
            response.status_code,
            (
                status.HTTP_404_NOT_FOUND,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_405_METHOD_NOT_ALLOWED,
            ),
        )
        row_b.refresh_from_db()
        self.assertNotEqual(getattr(row_b, "title", ""), "hijacked")


class TestDocumentsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/documents/"
    detail_url = staticmethod(lambda pk: f"/api/documents/{pk}/")

    def seed(self):
        from documents.models import Document

        a = Document.objects.create(
            project=self.project_a,
            document_type="brd",
            title="Alpha doc",
        )
        b = Document.objects.create(
            project=self.project_b,
            document_type="brd",
            title="Beta doc",
        )
        return a, b


class TestTasksIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/tasks/"
    detail_url = staticmethod(lambda pk: f"/api/tasks/{pk}/")

    def seed(self):
        from tasks.models import Task

        a = Task.objects.create(project=self.project_a, title="Alpha task")
        b = Task.objects.create(project=self.project_b, title="Beta task")
        return a, b


class TestTaskCommentsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/tasks/comments/"
    detail_url = staticmethod(lambda pk: f"/api/tasks/comments/{pk}/")

    def seed(self):
        from tasks.models import Task, TaskComment

        ta = Task.objects.create(project=self.project_a, title="Alpha task")
        tb = Task.objects.create(project=self.project_b, title="Beta task")
        a = TaskComment.objects.create(task=ta, content="Alpha comment")
        b = TaskComment.objects.create(task=tb, content="Beta comment")
        return a, b


class TestTaskAttachmentsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/tasks/attachments/"
    detail_url = staticmethod(lambda pk: f"/api/tasks/attachments/{pk}/")

    def seed(self):
        from tasks.models import Task, TaskAttachment

        ta = Task.objects.create(project=self.project_a, title="Alpha task")
        tb = Task.objects.create(project=self.project_b, title="Beta task")
        a = TaskAttachment.objects.create(
            task=ta,
            file=SimpleUploadedFile("a.txt", b"alpha"),
        )
        b = TaskAttachment.objects.create(
            task=tb,
            file=SimpleUploadedFile("b.txt", b"beta"),
        )
        return a, b


class TestWorkflowsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/workflows/"
    detail_url = staticmethod(lambda pk: f"/api/workflows/{pk}/")

    def seed(self):
        from workflows.models import Workflow

        a = Workflow.objects.create(
            project=self.project_a,
            name="Alpha workflow",
            trigger_event="task.created",
        )
        b = Workflow.objects.create(
            project=self.project_b,
            name="Beta workflow",
            trigger_event="task.created",
        )
        return a, b


class TestWorkflowExecutionsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/workflows/executions/"
    detail_url = staticmethod(lambda pk: f"/api/workflows/executions/{pk}/")

    def seed(self):
        from workflows.models import Workflow, WorkflowExecution

        wa = Workflow.objects.create(
            project=self.project_a,
            name="Alpha workflow",
            trigger_event="task.created",
        )
        wb = Workflow.objects.create(
            project=self.project_b,
            name="Beta workflow",
            trigger_event="task.created",
        )
        a = WorkflowExecution.objects.create(
            workflow=wa,
            entity_type="task",
            entity_id="1",
            initiated_by=self.user_a,
        )
        b = WorkflowExecution.objects.create(
            workflow=wb,
            entity_type="task",
            entity_id="2",
            initiated_by=self.user_b,
        )
        return a, b


class TestApprovalsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/approvals/"
    detail_url = staticmethod(lambda pk: f"/api/approvals/{pk}/")

    def seed(self):
        from approvals.models import Approval

        a = Approval.objects.create(
            project=self.project_a,
            entity_type="task",
            entity_id="1",
            title="Alpha approval",
        )
        b = Approval.objects.create(
            project=self.project_b,
            entity_type="task",
            entity_id="2",
            title="Beta approval",
        )
        return a, b


class TestRisksIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/risks/"
    detail_url = staticmethod(lambda pk: f"/api/risks/{pk}/")

    def seed(self):
        from risks.models import Risk

        a = Risk.objects.create(
            project=self.project_a,
            title="Alpha risk",
            description="Alpha description",
        )
        b = Risk.objects.create(
            project=self.project_b,
            title="Beta risk",
            description="Beta description",
        )
        return a, b


class TestIssuesIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/issues/"
    detail_url = staticmethod(lambda pk: f"/api/issues/{pk}/")

    def seed(self):
        from issues.models import Issue

        a = Issue.objects.create(project=self.project_a, title="Alpha issue")
        b = Issue.objects.create(project=self.project_b, title="Beta issue")
        return a, b


class TestReportsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/reports/"
    detail_url = staticmethod(lambda pk: f"/api/reports/{pk}/")

    def seed(self):
        from reports.models import Report

        a = Report.objects.create(
            project=self.project_a,
            title="Alpha report",
            content="Alpha content",
        )
        b = Report.objects.create(
            project=self.project_b,
            title="Beta report",
            content="Beta content",
        )
        return a, b


class TestMeetingsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/meetings/"
    detail_url = staticmethod(lambda pk: f"/api/meetings/{pk}/")

    def seed(self):
        from meetings.models import Meeting

        a = Meeting.objects.create(
            project=self.project_a,
            title="Alpha meeting",
            start_time=datetime(2026, 1, 1, 10, 0, tzinfo=tz.utc),
            organizer=self.user_a,
        )
        a.participants.add(self.user_a)
        b = Meeting.objects.create(
            project=self.project_b,
            title="Beta meeting",
            start_time=datetime(2026, 1, 1, 10, 0, tzinfo=tz.utc),
            organizer=self.user_b,
        )
        b.participants.add(self.user_b)
        return a, b


class TestConversationsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/chat/conversations/"
    detail_url = staticmethod(lambda pk: f"/api/chat/conversations/{pk}/")

    def seed(self):
        from chat.models import Conversation

        a = Conversation.objects.create(
            project=self.project_a,
            title="Alpha chat",
            conversation_type="project",
            created_by=self.user_a,
        )
        a.participants.add(self.user_a)
        b = Conversation.objects.create(
            project=self.project_b,
            title="Beta chat",
            conversation_type="project",
            created_by=self.user_b,
        )
        b.participants.add(self.user_b)
        return a, b


class TestMessagesIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/chat/messages/"
    detail_url = staticmethod(lambda pk: f"/api/chat/messages/{pk}/")

    def seed(self):
        from chat.models import Conversation, Message

        ca = Conversation.objects.create(
            project=self.project_a,
            title="Alpha chat",
            conversation_type="project",
            created_by=self.user_a,
        )
        ca.participants.add(self.user_a)
        cb = Conversation.objects.create(
            project=self.project_b,
            title="Beta chat",
            conversation_type="project",
            created_by=self.user_b,
        )
        cb.participants.add(self.user_b)
        a = Message.objects.create(conversation=ca, sender=self.user_a, content="hi")
        b = Message.objects.create(conversation=cb, sender=self.user_b, content="yo")
        return a, b


class TestKnowledgeBaseIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/knowledge-base/"
    detail_url = staticmethod(lambda pk: f"/api/knowledge-base/{pk}/")

    def seed(self):
        from knowledge_base.models import KnowledgeBase

        a = KnowledgeBase.objects.create(
            project=self.project_a,
            title="Alpha kb",
            content="Alpha content",
            created_by=self.user_a,
        )
        b = KnowledgeBase.objects.create(
            project=self.project_b,
            title="Beta kb",
            content="Beta content",
            created_by=self.user_b,
        )
        return a, b


class TestDeploymentsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/deployments/"
    detail_url = staticmethod(lambda pk: f"/api/deployments/{pk}/")

    def seed(self):
        from deployments.models import Deployment

        a = Deployment.objects.create(
            project=self.project_a,
            title="Alpha deploy",
            version="1.0.0",
        )
        b = Deployment.objects.create(
            project=self.project_b,
            title="Beta deploy",
            version="1.0.0",
        )
        return a, b


class TestArchitectureDiagramsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/architecture/diagrams/"
    detail_url = staticmethod(lambda pk: f"/api/architecture/diagrams/{pk}/")

    def seed(self):
        from architecture.models import ArchitectureDiagram

        a = ArchitectureDiagram.objects.create(
            project=self.project_a,
            title="Alpha diagram",
        )
        b = ArchitectureDiagram.objects.create(
            project=self.project_b,
            title="Beta diagram",
        )
        return a, b


class TestTechnologyStackIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/architecture/tech-stack/"
    detail_url = staticmethod(lambda pk: f"/api/architecture/tech-stack/{pk}/")

    def seed(self):
        from architecture.models import TechnologyStack

        a = TechnologyStack.objects.create(
            project=self.project_a,
            name="Alpha stack",
        )
        b = TechnologyStack.objects.create(
            project=self.project_b,
            name="Beta stack",
        )
        return a, b


class TestReviewsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/reviews/"
    detail_url = staticmethod(lambda pk: f"/api/reviews/{pk}/")

    def seed(self):
        from reviews.models import Review

        a = Review.objects.create(
            project=self.project_a,
            title="Alpha review",
            reviewer=self.user_a,
        )
        b = Review.objects.create(
            project=self.project_b,
            title="Beta review",
            reviewer=self.user_b,
        )
        return a, b


class TestSecurityChecklistsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/security/checklists/"
    detail_url = staticmethod(lambda pk: f"/api/security/checklists/{pk}/")

    def seed(self):
        from security.models import SecurityChecklist

        a = SecurityChecklist.objects.create(
            project=self.project_a,
            title="Alpha checklist",
        )
        b = SecurityChecklist.objects.create(
            project=self.project_b,
            title="Beta checklist",
        )
        return a, b


class TestVulnerabilityReportsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/security/vulnerabilities/"
    detail_url = staticmethod(lambda pk: f"/api/security/vulnerabilities/{pk}/")

    def seed(self):
        from security.models import VulnerabilityReport

        a = VulnerabilityReport.objects.create(
            project=self.project_a,
            title="Alpha vuln",
            description="Alpha description",
        )
        b = VulnerabilityReport.objects.create(
            project=self.project_b,
            title="Beta vuln",
            description="Beta description",
        )
        return a, b


class TestIntegrationsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/integrations/"
    detail_url = staticmethod(lambda pk: f"/api/integrations/{pk}/")

    def seed(self):
        from integrations.models import Integration

        a = Integration.objects.create(
            project=self.project_a,
            name="Alpha integration",
            integration_type="slack",
        )
        b = Integration.objects.create(
            project=self.project_b,
            name="Beta integration",
            integration_type="slack",
        )
        return a, b


class TestMonitoringAlertsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/monitoring/alerts/"
    detail_url = staticmethod(lambda pk: f"/api/monitoring/alerts/{pk}/")

    def seed(self):
        from monitoring.models import MonitoringAlert

        a = MonitoringAlert.objects.create(
            project=self.project_a,
            title="Alpha alert",
            message="Alpha message",
        )
        b = MonitoringAlert.objects.create(
            project=self.project_b,
            title="Beta alert",
            message="Beta message",
        )
        return a, b


class TestSystemMetricsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/monitoring/metrics/"
    detail_url = staticmethod(lambda pk: f"/api/monitoring/metrics/{pk}/")

    def seed(self):
        from monitoring.models import SystemMetric

        a = SystemMetric.objects.create(
            project=self.project_a,
            metric_name="cpu_usage",
            metric_value="12.5",
        )
        b = SystemMetric.objects.create(
            project=self.project_b,
            metric_name="cpu_usage",
            metric_value="99.9",
        )
        return a, b


class TestDiscoveryIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/discovery/"
    detail_url = staticmethod(lambda pk: f"/api/discovery/{pk}/")

    def seed(self):
        from discovery.models import Discovery

        a = Discovery.objects.create(
            project=self.project_a,
            created_by=self.user_a,
        )
        b = Discovery.objects.create(
            project=self.project_b,
            created_by=self.user_b,
        )
        return a, b


class TestProjectMembersIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/project-members/"
    detail_url = staticmethod(lambda pk: f"/api/project-members/{pk}/")

    def seed(self):
        from roles.models import Role
        from project_members.models import ProjectMember

        role = Role.objects.get_or_create(
            role_key="business_analyst",
            defaults={"display_name": "Business Analyst"},
        )[0]
        a = ProjectMember.objects.create(
            project=self.project_a,
            user=self.user_a,
            role=role,
        )
        b = ProjectMember.objects.create(
            project=self.project_b,
            user=self.user_b,
            role=role,
        )
        return a, b


class TestDashboardWidgetsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/dashboard/widgets/"
    detail_url = staticmethod(lambda pk: f"/api/dashboard/widgets/{pk}/")

    def seed(self):
        from dashboard.models import DashboardWidget

        a = DashboardWidget.objects.create(
            project=self.project_a,
            title="Alpha widget",
            widget_type="project_summary",
            owner=self.user_a,
        )
        b = DashboardWidget.objects.create(
            project=self.project_b,
            title="Beta widget",
            widget_type="project_summary",
            owner=self.user_b,
        )
        return a, b


class TestAuditLogsIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/audit-logs/"
    detail_url = staticmethod(lambda pk: f"/api/audit-logs/{pk}/")

    def seed(self):
        from audit_logs.models import AuditLog

        a = AuditLog.objects.create(
            company=self.company_a,
            user=self.user_a,
            action="create",
            entity_type="task",
            entity_id="1",
            entity_name="Alpha entity",
        )
        b = AuditLog.objects.create(
            company=self.company_b,
            user=self.user_b,
            action="create",
            entity_type="task",
            entity_id="2",
            entity_name="Beta entity",
        )
        return a, b


class TestAIAssessmentWriteIsolation(TenantIsolationBase):
    """
    A POST that points a tenant-scoped FK at another company's row must be
    rejected at write time, even though list/detail reads are already scoped.
    """

    def _create(self, project):
        return self.client.post(
            "/api/ai-engine/assessments/",
            {"project": project.pk},
            format="json",
        )

    def test_create_with_own_project_succeeds(self):
        response = self._create(self.project_a)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_with_foreign_project_rejected(self):
        response = self._create(self.project_b)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            response.json().get("success", True),
            "The API should not silently accept a cross-tenant FK.",
        )

    def test_update_steering_project_to_foreign_company_rejected(self):
        from ai_engine.models import AIAssessment

        own = AIAssessment.objects.create(project=self.project_a)
        response = self.client.patch(
            f"/api/ai-engine/assessments/{own.pk}/",
            {"project": self.project_b.pk},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        own.refresh_from_db()
        self.assertEqual(own.project_id, self.project_a.pk)


class TestDocumentTemplatesIsolation(TenantIsolationBase, _EndpointTestMixin):
    list_url = "/api/document-templates/"
    detail_url = staticmethod(lambda pk: f"/api/document-templates/{pk}/")

    def seed(self):
        from document_templates.models import DocumentTemplate

        a = DocumentTemplate.objects.create(
            project=self.project_a,
            name="Alpha template",
            category="proposal",
            file=SimpleUploadedFile("a.docx", b"alpha"),
            original_filename="a.docx",
        )
        b = DocumentTemplate.objects.create(
            project=self.project_b,
            name="Beta template",
            category="proposal",
            file=SimpleUploadedFile("b.docx", b"beta"),
            original_filename="b.docx",
        )
        return a, b

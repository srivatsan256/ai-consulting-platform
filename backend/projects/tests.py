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
from projects.models import LevelModule, Milestone, Project, ProjectPhase


class ProjectModelTests(APITestCase):
    def test_default_status_is_planning(self):
        company = create_company(name="Model Corp")
        project = create_project(company, name="Model Project")
        self.assertEqual(project.status, "planning")
        self.assertEqual(project.current_level, 1)
        self.assertEqual(project.progress, 0)

    def test_string_representation(self):
        company = create_company(name="Model Corp")
        project = create_project(company, name="Name Me")
        self.assertEqual(str(project), "Name Me")


class ProjectViewSetTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="pm", email="pm@example.com")
        self.company = create_company(name="Project Corp")
        create_member(self.user, self.company)
        self.list_url = reverse("project-list")

    def test_requires_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_project(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {
                "project_name": "AI Migration",
                "description": "Move to AI stack",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project = Project.objects.get(project_name="AI Migration")
        self.assertEqual(project.company, self.company)

    def test_update_project(self):
        project = create_project(self.company, name="Old")
        authenticate(self.client, self.user)
        response = self.client.patch(
            reverse("project-detail", args=[project.pk]),
            {"project_name": "New"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project.refresh_from_db()
        self.assertEqual(project.project_name, "New")

    def test_delete_project(self):
        project = create_project(self.company, name="Doomed")
        authenticate(self.client, self.user)
        response = self.client.delete(
            reverse("project-detail", args=[project.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())


class ProjectTenantScopingTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="scoped", email="scoped@example.com")
        self.company = create_company(name="My Corp")
        create_member(self.user, self.company)

        self.other_user = create_user(
            username="other_scoped",
            email="other_scoped@example.com",
        )
        self.other_company = create_company(name="Other Corp")
        create_member(self.other_user, self.other_company)

    def test_tenant_views_filter_projects_by_company(self):
        mine = create_project(self.company, name="Mine")
        create_project(self.other_company, name="Theirs")

        authenticate(self.client, self.user)
        response = self.client.get("/api/projects/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [p["project_name"] for p in response.data["results"]]
        self.assertIn("Mine", names)
        self.assertNotIn("Theirs", names)

    def test_detail_view_rejects_other_tenants_project(self):
        their_project = create_project(self.other_company, name="Secret")
        authenticate(self.client, self.user)
        response = self.client.get(f"/api/projects/{their_project.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_view_allows_own_project(self):
        mine = create_project(self.company, name="Visible")
        authenticate(self.client, self.user)
        response = self.client.get(f"/api/projects/{mine.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["project_name"], "Visible")

    def test_detail_patch_allows_own_project(self):
        mine = create_project(self.company, name="Patchable")
        authenticate(self.client, self.user)
        response = self.client.patch(
            f"/api/projects/{mine.pk}/",
            {"description": "updated"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_rejects_other_tenants_project(self):
        their_project = create_project(self.other_company, name="Secret2")
        authenticate(self.client, self.user)
        response = self.client.delete(f"/api/projects/{their_project.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProjectPhaseAndMilestoneTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="phases", email="phases@example.com")
        self.company = create_company(name="Phase Corp")
        create_member(self.user, self.company)
        self.project = create_project(self.company, name="Phase Project")
        authenticate(self.client, self.user)

    def test_create_phase(self):
        response = self.client.post(
            reverse("projectphase-list"),
            {
                "project": self.project.id,
                "phase_name": "Discovery",
                "order": 1,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ProjectPhase.objects.filter(phase_name="Discovery").exists()
        )

    def test_create_milestone(self):
        response = self.client.post(
            reverse("milestone-list"),
            {
                "project": self.project.id,
                "title": "Kickoff",
                "due_date": "2025-06-01",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Milestone.objects.filter(title="Kickoff").exists())

    def test_phase_ordering_by_order(self):
        ProjectPhase.objects.create(
            project=self.project,
            phase_name="Second",
            order=2,
        )
        ProjectPhase.objects.create(
            project=self.project,
            phase_name="First",
            order=1,
        )
        response = self.client.get(reverse("projectphase-list"))
        names = [p["phase_name"] for p in response.data["results"]]
        self.assertEqual(names, ["First", "Second"])


class LevelModuleTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="levels", email="levels@example.com")
        authenticate(self.client, self.user)

    def test_level_module_list(self):
        LevelModule.objects.create(
            level=1,
            title="Initial",
            required_documents=[{"doc_type": "vision", "label": "Vision"}],
        )
        response = self.client.get(reverse("level-modules"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["level"], 1)

    def test_required_doc_status_endpoint(self):
        company = create_company(name="Readiness Corp")
        create_member(self.user, company)
        LevelModule.objects.create(
            level=1,
            title="Initial",
            required_documents=[{"doc_type": "vision", "label": "Vision"}],
        )
        project = create_project(company, name="Readiness Project")

        response = self.client.get(
            f"/api/projects/{project.pk}/required_doc_status/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["current_level"], 1)
        self.assertEqual(len(response.data["required_docs"]), 1)
        self.assertFalse(response.data["required_docs"][0]["has_passed"])

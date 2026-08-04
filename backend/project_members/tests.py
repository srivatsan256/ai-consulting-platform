from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.tests_helpers import (
    authenticate,
    create_company,
    create_member,
    create_project,
    create_user,
    get_role,
)
from project_members.models import ProjectMember


class ProjectMemberModelTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="powner", email="powner@example.com")
        self.company = create_company(name="PM Corp")
        create_member(self.user, self.company)
        self.project = create_project(self.company, name="PM Project")

    def test_membership_unique_per_project_and_user(self):
        ProjectMember.objects.create(
            project=self.project,
            user=self.user,
            role=get_role(),
        )
        with self.assertRaises(Exception):
            ProjectMember.objects.create(
                project=self.project,
                user=self.user,
                role=get_role(),
            )

    def test_string_representation(self):
        member = ProjectMember.objects.create(
            project=self.project,
            user=self.user,
            role=get_role(),
        )
        self.assertIn(self.project.project_name, str(member))


class ProjectMemberViewSetTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="pmember", email="pmember@example.com")
        self.company = create_company(name="PM API Corp")
        create_member(self.user, self.company)
        self.project = create_project(self.company, name="PM API Project")
        self.list_url = reverse("projectmember-list")

    def test_requires_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_project_member(self):
        member_user = create_user(username="dev", email="dev@example.com")
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {
                "project": self.project.id,
                "user": member_user.id,
                "role": get_role().id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ProjectMember.objects.filter(
                project=self.project,
                user=member_user,
            ).exists()
        )

    def test_delete_project_member(self):
        member = ProjectMember.objects.create(
            project=self.project,
            user=self.user,
            role=get_role(),
        )
        authenticate(self.client, self.user)
        response = self.client.delete(
            reverse("projectmember-detail", args=[member.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            ProjectMember.objects.filter(pk=member.pk).exists()
        )

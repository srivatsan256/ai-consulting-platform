from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.tests_helpers import (
    authenticate,
    create_company,
    create_member,
    create_user,
)
from departments.models import Department
from teams.models import Team, TeamMember


class TeamModelTests(APITestCase):
    def setUp(self):
        self.company = create_company(name="Team Corp")
        self.department = Department.objects.create(
            company=self.company,
            name="Engineering",
            code="ENG",
        )

    def test_team_name_unique_per_department(self):
        Team.objects.create(
            department=self.department,
            team_name="Platform",
        )
        with self.assertRaises(Exception):
            Team.objects.create(
                department=self.department,
                team_name="Platform",
            )

    def test_string_representation(self):
        team = Team.objects.create(
            department=self.department,
            team_name="AI Guild",
        )
        self.assertEqual(str(team), "AI Guild")


class TeamViewSetTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="team_user", email="team@example.com")
        self.company = create_company(name="Team API Corp")
        create_member(self.user, self.company)
        self.department = Department.objects.create(
            company=self.company,
            name="Engineering",
            code="ENG",
        )
        self.list_url = reverse("team-list")

    def test_requires_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_team(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {
                "department": self.department.id,
                "team_name": "Backend",
                "description": "API team",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Team.objects.filter(team_name="Backend").exists()
        )

    def test_duplicate_team_name_rejected(self):
        Team.objects.create(
            department=self.department,
            team_name="Backend",
        )
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {"department": self.department.id, "team_name": "Backend"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_by_department(self):
        other_dept = Department.objects.create(
            company=self.company,
            name="Finance",
            code="FIN",
        )
        Team.objects.create(
            department=self.department,
            team_name="Backend",
        )
        Team.objects.create(
            department=other_dept,
            team_name="FP&A",
        )
        authenticate(self.client, self.user)
        response = self.client.get(
            self.list_url,
            {"department": self.department.id},
        )
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["team_name"], "Backend")

    def test_delete_team(self):
        team = Team.objects.create(
            department=self.department,
            team_name="Doomed",
        )
        authenticate(self.client, self.user)
        response = self.client.delete(
            reverse("team-detail", args=[team.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Team.objects.filter(pk=team.pk).exists())

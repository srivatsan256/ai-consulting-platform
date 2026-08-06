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


class DepartmentModelTests(APITestCase):
    def setUp(self):
        self.company = create_company(name="Dept Corp")

    def test_code_unique_per_company(self):
        Department.objects.create(
            company=self.company,
            name="Engineering",
            code="ENG",
        )
        with self.assertRaises(Exception):
            Department.objects.create(
                company=self.company,
                name="Engineering Again",
                code="ENG",
            )

    def test_name_unique_per_company(self):
        Department.objects.create(
            company=self.company,
            name="Finance",
            code="FIN",
        )
        with self.assertRaises(Exception):
            Department.objects.create(
                company=self.company,
                name="Finance",
                code="FIN2",
            )

    def test_same_code_allowed_across_companies(self):
        other = create_company(name="Other Dept Corp")
        Department.objects.create(
            company=self.company,
            name="Sales",
            code="SAL",
        )
        dept = Department.objects.create(
            company=other,
            name="Sales",
            code="SAL",
        )
        self.assertEqual(dept.code, "SAL")


class DepartmentViewSetTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="dept_user", email="dept@example.com")
        self.company = create_company(name="Dept API Corp")
        create_member(self.user, self.company)
        self.list_url = reverse("department-list")

    def test_requires_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_department(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {
                "company": self.company.id,
                "name": "Engineering",
                "code": "ENG",
                "description": "Builds things",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Department.objects.filter(code="ENG").exists()
        )

    def test_retrieve_department(self):
        dept = Department.objects.create(
            company=self.company,
            name="Research",
            code="RES",
        )
        authenticate(self.client, self.user)
        response = self.client.get(
            reverse("department-detail", args=[dept.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Research")

    def test_update_department(self):
        dept = Department.objects.create(
            company=self.company,
            name="Research",
            code="RES",
        )
        authenticate(self.client, self.user)
        response = self.client.patch(
            reverse("department-detail", args=[dept.pk]),
            {"status": "inactive"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dept.refresh_from_db()
        self.assertEqual(dept.status, "inactive")

    def test_filter_by_company(self):
        other = create_company(name="Unrelated Co")
        Department.objects.create(
            company=self.company,
            name="Mine",
            code="MIN",
        )
        Department.objects.create(
            company=other,
            name="Theirs",
            code="THE",
        )
        authenticate(self.client, self.user)
        response = self.client.get(
            self.list_url,
            {"company": self.company.id},
        )
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Mine")

    def test_delete_department(self):
        dept = Department.objects.create(
            company=self.company,
            name="Doomed",
            code="DOO",
        )
        authenticate(self.client, self.user)
        response = self.client.delete(
            reverse("department-detail", args=[dept.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Department.objects.filter(pk=dept.pk).exists())

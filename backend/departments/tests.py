from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.tests_helpers import (
    authenticate,
    create_company,
    create_member,
    create_user,
)
from departments.models import Department, DepartmentMember


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


class DepartmentMemberModelTests(APITestCase):
    def setUp(self):
        self.company = create_company(name="Member Corp")
        self.dept = Department.objects.create(
            company=self.company,
            name="Engineering",
            code="ENG",
        )
        self.user = create_user(username="dm_user", email="dm@example.com")
        create_member(self.user, self.company)

    def test_unique_user_department(self):
        DepartmentMember.objects.create(user=self.user, department=self.dept)
        with self.assertRaises(Exception):
            DepartmentMember.objects.create(
                user=self.user,
                department=self.dept,
            )

    def test_string_representation(self):
        member = DepartmentMember.objects.create(
            user=self.user,
            department=self.dept,
        )
        self.assertEqual(str(member), "dm@example.com @ Engineering")


class DepartmentMemberViewSetTests(APITestCase):
    def setUp(self):
        self.company = create_company(name="Member API Corp")
        self.admin = create_user(username="dm_admin", email="dm_admin@example.com")
        create_member(self.admin, self.company, role_key="company_admin")
        self.regular = create_user(username="dm_regular", email="dm_regular@example.com")
        create_member(self.regular, self.company, role_key="business_analyst")
        self.head = create_user(username="dm_head", email="dm_head@example.com")
        create_member(self.head, self.company, role_key="project_manager")
        self.member = create_user(username="dm_member", email="dm_member@example.com")
        create_member(self.member, self.company, role_key="qa_test_engineer")

        self.dept = Department.objects.create(
            company=self.company,
            name="Research",
            code="RES",
            head=self.head,
        )
        self.other_dept = Department.objects.create(
            company=self.company,
            name="Finance",
            code="FIN",
        )
        self.list_url = reverse("department-member-list")

    def test_admin_can_add_member(self):
        authenticate(self.client, self.admin)
        response = self.client.post(
            self.list_url,
            {"user": self.member.id, "department": self.dept.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            DepartmentMember.objects.filter(
                user=self.member,
                department=self.dept,
            ).exists()
        )

    def test_department_head_can_add_member(self):
        authenticate(self.client, self.head)
        response = self.client.post(
            self.list_url,
            {"user": self.member.id, "department": self.dept.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_regular_member_cannot_add_member(self):
        authenticate(self.client, self.regular)
        response = self.client.post(
            self.list_url,
            {"user": self.member.id, "department": self.dept.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_head_cannot_add_to_other_department(self):
        authenticate(self.client, self.head)
        response = self.client.post(
            self.list_url,
            {"user": self.member.id, "department": self.other_dept.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_add_user_from_other_company(self):
        outsider_company = create_company(name="Other Corp")
        outsider = create_user(username="dm_outsider", email="dm_outsider@example.com")
        create_member(outsider, outsider_company)
        authenticate(self.client, self.admin)
        response = self.client.post(
            self.list_url,
            {"user": outsider.id, "department": self.dept.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_member_by_admin(self):
        DepartmentMember.objects.create(user=self.member, department=self.dept)
        authenticate(self.client, self.admin)
        member_pk = DepartmentMember.objects.get(
            user=self.member,
            department=self.dept,
        ).pk
        response = self.client.delete(
            reverse("department-member-detail", args=[member_pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            DepartmentMember.objects.filter(
                user=self.member,
                department=self.dept,
            ).exists()
        )

    def test_remove_member_denied_for_regular_member(self):
        DepartmentMember.objects.create(user=self.member, department=self.dept)
        authenticate(self.client, self.regular)
        member_pk = DepartmentMember.objects.get(
            user=self.member,
            department=self.dept,
        ).pk
        response = self.client.delete(
            reverse("department-member-detail", args=[member_pk])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mine_returns_own_departments(self):
        DepartmentMember.objects.create(user=self.member, department=self.dept)
        authenticate(self.client, self.member)
        response = self.client.get(reverse("department-member-mine"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["department"], self.dept.id)

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
from tasks.models import Task, TaskComment


class TaskModelTests(APITestCase):
    def test_defaults(self):
        company = create_company(name="Task Corp")
        project = create_project(company, name="Task Project")
        task = Task.objects.create(
            project=project,
            title="Write tests",
        )
        self.assertEqual(task.status, "todo")
        self.assertEqual(task.priority, "medium")

    def test_subtask_relationship(self):
        company = create_company(name="Sub Task Corp")
        project = create_project(company, name="Sub Project")
        parent = Task.objects.create(
            project=project,
            title="Parent",
        )
        child = Task.objects.create(
            project=project,
            title="Child",
            parent=parent,
        )
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.subtasks.all())


class TaskViewSetTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="task_user", email="task@example.com")
        self.company = create_company(name="Task API Corp")
        create_member(self.user, self.company)
        self.project = create_project(self.company, name="Task API Project")
        self.task = Task.objects.create(
            project=self.project,
            title="Initial task",
            created_by=self.user,
        )
        self.list_url = reverse("task-list")

    def test_requires_authentication(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {
                "project": self.project.id,
                "title": "New task",
                "status": "in_progress",
                "priority": "high",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Task.objects.filter(title="New task").exists())

    def test_task_assignment_creates_notification(self):
        assignee = create_user(
            username="assignee",
            email="assignee@example.com",
        )
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {
                "project": self.project.id,
                "title": "Assigned task",
                "assigned_to": assignee.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        from notifications.models import Notification

        notification = Notification.objects.filter(
            recipient=assignee,
            entity_type="task",
        ).first()
        self.assertIsNotNone(notification)
        self.assertIn("Assigned task", notification.title)

    def test_complete_action_sets_done(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            reverse("task-complete", args=[self.task.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "done")
        self.assertIsNotNone(self.task.completed_at)

    def test_create_subtask(self):
        authenticate(self.client, self.user)
        response = self.client.post(
            self.list_url,
            {
                "project": self.project.id,
                "parent": self.task.id,
                "title": "Subtask",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_task(self):
        authenticate(self.client, self.user)
        response = self.client.delete(
            reverse("task-detail", args=[self.task.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())


class TaskCommentTests(APITestCase):
    def setUp(self):
        self.user = create_user(username="commenter", email="c@example.com")
        self.company = create_company(name="Comment Corp")
        create_member(self.user, self.company)
        self.project = create_project(self.company, name="Comment Project")
        self.task = Task.objects.create(
            project=self.project,
            title="Commented",
        )
        authenticate(self.client, self.user)

    def test_create_comment_via_task_action(self):
        response = self.client.post(
            reverse("task-task-comments", args=[self.task.pk]),
            {"content": "Looking good"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            TaskComment.objects.filter(content="Looking good").exists()
        )

    def test_list_comments_via_task_action(self):
        TaskComment.objects.create(
            task=self.task,
            author=self.user,
            content="Nice work",
        )
        response = self.client.get(
            reverse("task-task-comments", args=[self.task.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_comment_viewset_requires_content(self):
        response = self.client.post(
            reverse("taskcomment-list"),
            {"task": self.task.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

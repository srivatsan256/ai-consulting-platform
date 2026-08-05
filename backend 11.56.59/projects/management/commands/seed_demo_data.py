"""
Seed demo users, companies, roles and memberships so the frontend's demo
accounts can log in against the real backend.

Accounts mirror frontend/src/constants/roles.js and all share the password
``password123``.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from companies.models import Company
from company_members.models import CompanyMember
from projects.models import Project
from roles.models import Role

User = get_user_model()

DEMO_USERS = [
    # Admin roles -> RequirementAI Consulting
    ("super_admin", "Alexander Vance", "superadmin@requirementai.com", "Super Admin", "admin"),
    ("company_admin", "Sarah Chen", "companyadmin@requirementai.com", "Company Admin", "admin"),
    ("project_manager", "Michael Vance", "pm@requirementai.com", "Project Manager", "admin"),
    ("business_analyst", "Emily Watson", "ba@requirementai.com", "Business Analyst", "admin"),
    ("solution_architect", "David Kross", "architect@requirementai.com", "Solution Architect", "admin"),
    ("ai_ml_engineer", "Elena Rostova", "ai_eng@requirementai.com", "AI/ML Engineer", "admin"),
    ("backend_developer", "Marcus Aurelius", "backend@requirementai.com", "Backend Developer", "admin"),
    ("frontend_developer", "Lisa Simpson", "frontend@requirementai.com", "Frontend Developer", "admin"),
    ("qa_test_engineer", "Thomas Edison", "qa@requirementai.com", "QA / Test Engineer", "admin"),
    ("security_consultant", "Grace Hopper", "security@requirementai.com", "Security Consultant", "admin"),
    ("devops_engineer", "Alan Turing", "devops@requirementai.com", "DevOps Engineer", "admin"),
    ("document_reviewer", "Ada Lovelace", "reviewer@requirementai.com", "Document Reviewer", "admin"),
    # Client roles -> Acme Corp
    ("client_admin", "John Smith", "client_admin@acmecorp.com", "Client Admin", "client"),
    ("client_sme", "Robert Kiyosaki", "client_sme@acmecorp.com", "Client Department Owner (SME)", "client"),
    ("client_reviewer", "Arthur Pendragon", "client_reviewer@acmecorp.com", "Client Reviewer", "client"),
    ("business_sponsor", "Bruce Wayne", "sponsor@acmecorp.com", "Business Sponsor", "client"),
    ("viewer", "Clark Kent", "viewer@acmecorp.com", "Viewer", "client"),
]

PASSWORD = "password123"

DEMO_PROJECTS = [
    # RequirementAI Consulting projects
    {
        "company_name": "RequirementAI Consulting",
        "project_name": "Enterprise AI Adoption Roadmap",
        "description": "Define the phased adoption roadmap for enterprise AI capabilities.",
        "industry": "Technology",
        "objectives": "Establish a governed AI adoption roadmap across departments.",
        "team_members": "Sarah Chen, Michael Vance, Elena Rostova",
        "expected_timeline": "6 weeks",
        "status": "development",
        "priority": "high",
        "progress": 35,
    },
    # Acme Corp projects
    {
        "company_name": "Acme Corp",
        "project_name": "Acme ERP Migration",
        "description": "Migrate on-premise ERP to a cloud platform.",
        "industry": "Retail",
        "objectives": "Migrate ERP to cloud with 99.9% uptime and 20% cost savings.",
        "team_members": "John Smith, Robert Kiyosaki",
        "expected_timeline": "12 weeks",
        "status": "discovery",
        "priority": "medium",
        "progress": 10,
    },
    {
        "company_name": "Acme Corp",
        "project_name": "Customer 360 Platform",
        "description": "Unify customer data across sales, support and marketing.",
        "industry": "Retail",
        "objectives": "Deliver a single customer view to drive retention.",
        "team_members": "John Smith, Arthur Pendragon",
        "expected_timeline": "8 weeks",
        "status": "planning",
        "priority": "high",
        "progress": 20,
    },
]


class Command(BaseCommand):
    help = "Seed demo companies, roles, users and memberships."

    def handle(self, *args, **options):
        consulting, _ = Company.objects.get_or_create(
            company_name="RequirementAI Consulting",
            defaults={
                "industry": "Consulting",
                "business_description": "AI consulting delivery platform operator.",
            },
        )
        acme, _ = Company.objects.get_or_create(
            company_name="Acme Corp",
            defaults={
                "industry": "Retail",
                "business_description": "Demo enterprise client.",
            },
        )

        company_for = {
            "admin": consulting,
            "client": acme,
        }

        created_users = 0
        created_members = 0

        for role_key, full_name, email, display_name, role_type in DEMO_USERS:
            role, _ = Role.objects.get_or_create(
                role_key=role_key,
                defaults={"display_name": display_name},
            )
            role.display_name = display_name
            role.save()

            first_name, _, last_name = full_name.partition(" ")

            user, user_created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_active": True,
                    "is_staff": role_key == "super_admin",
                    "is_superuser": role_key == "super_admin",
                },
            )
            if user_created:
                user.set_password(PASSWORD)
                user.save()
                created_users += 1

            membership, member_created = CompanyMember.objects.get_or_create(
                user=user,
                company=company_for[role_type],
                defaults={
                    "role": role,
                    "is_primary": True,
                    "is_active": True,
                },
            )
            if member_created:
                created_members += 1

        companies = {c.company_name: c for c in Company.objects.all()}
        created_projects = 0
        for spec in DEMO_PROJECTS:
            company = companies[spec["company_name"]]
            _, created = Project.objects.get_or_create(
                company=company,
                project_name=spec["project_name"],
                defaults={
                    "description": spec["description"],
                    "industry": spec["industry"],
                    "objectives": spec["objectives"],
                    "team_members": spec["team_members"],
                    "expected_timeline": spec["expected_timeline"],
                    "status": spec["status"],
                    "priority": spec["priority"],
                    "progress": spec["progress"],
                    "start_date": timezone.now().date(),
                },
            )
            if created:
                created_projects += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded demo data: {created_users} users created, "
                f"{created_members} memberships created, "
                f"{created_projects} projects created."
            )
        )
        self.stdout.write("All demo accounts use the password 'password123'.")

"""
Seed the five level modules used by the level-based verification flow.
"""

from django.core.management.base import BaseCommand

from projects.models import LevelModule

LEVEL_MODULES = [
    {
        "level": 1,
        "title": "Discovery & Requirements",
        "description": (
            "Business discovery and initial requirements capture. The BRD "
            "must document the business context before functional work begins."
        ),
        "icon": "explore",
        "must_include": [
            {"id": 101, "text": "Business objectives"},
            {"id": 102, "text": "Executive summary"},
            {"id": 103, "text": "Stakeholders"},
            {"id": 104, "text": "Project scope"},
            {"id": 105, "text": "Success metrics"},
        ],
        "recommended": [
            {"id": 106, "text": "Budget"},
            {"id": 107, "text": "Timeline"},
            {"id": 108, "text": "Risks"},
        ],
        "required_documents": [
            {"doc_type": "BRD", "label": "Business Requirements Document"},
        ],
        "required_count": 5,
    },
    {
        "level": 2,
        "title": "Functional Requirements",
        "description": (
            "Functional requirements must be captured in an FRD with user "
            "stories and workflows before detailed design."
        ),
        "icon": "manage_search",
        "must_include": [
            {"id": 201, "text": "Functional requirements"},
            {"id": 202, "text": "User stories"},
            {"id": 203, "text": "Use cases"},
            {"id": 204, "text": "Data requirements"},
            {"id": 205, "text": "Workflow"},
        ],
        "recommended": [
            {"id": 206, "text": "Non-functional requirements"},
            {"id": 207, "text": "Interface requirements"},
        ],
        "required_documents": [
            {"doc_type": "FRD", "label": "Functional Requirements Document"},
        ],
        "required_count": 5,
    },
    {
        "level": 3,
        "title": "Product & Solution Design",
        "description": (
            "The PRD must define the product behaviour, personas and "
            "acceptance criteria before build work is approved."
        ),
        "icon": "precision_manufacturing",
        "must_include": [
            {"id": 301, "text": "Product requirements"},
            {"id": 302, "text": "User personas"},
            {"id": 303, "text": "Acceptance criteria"},
            {"id": 304, "text": "UX design"},
            {"id": 305, "text": "API design"},
        ],
        "recommended": [
            {"id": 306, "text": "Security requirements"},
            {"id": 307, "text": "Integration requirements"},
        ],
        "required_documents": [
            {"doc_type": "PRD", "label": "Product Requirements Document"},
        ],
        "required_count": 5,
    },
    {
        "level": 4,
        "title": "Architecture & Security",
        "description": (
            "The solution architecture, data model and security controls "
            "must be documented and signed off."
        ),
        "icon": "account_tree",
        "must_include": [
            {"id": 401, "text": "Solution architecture"},
            {"id": 402, "text": "Data model"},
            {"id": 403, "text": "Security controls"},
            {"id": 404, "text": "Deployment plan"},
            {"id": 405, "text": "Monitoring plan"},
        ],
        "recommended": [
            {"id": 406, "text": "Disaster recovery"},
            {"id": 407, "text": "Performance targets"},
        ],
        "required_documents": [
            {"doc_type": "ARCHITECTURE", "label": "Architecture Document"},
            {"doc_type": "SECURITY", "label": "Security Document"},
        ],
        "required_count": 5,
    },
    {
        "level": 5,
        "title": "Operations & Optimization",
        "description": (
            "Operational procedures, runbooks and continuous improvement "
            "plans must be in place for ongoing optimisation."
        ),
        "icon": "auto_awesome",
        "must_include": [
            {"id": 501, "text": "Operating procedures"},
            {"id": 502, "text": "Runbooks"},
            {"id": 503, "text": "SLA definitions"},
            {"id": 504, "text": "Continuous improvement"},
            {"id": 505, "text": "Feedback loop"},
        ],
        "recommended": [
            {"id": 506, "text": "Training plan"},
            {"id": 507, "text": "Cost optimization"},
        ],
        "required_documents": [
            {"doc_type": "SOP", "label": "Standard Operating Procedure"},
            {"doc_type": "TEST_PLAN", "label": "Test Plan"},
        ],
        "required_count": 5,
    },
]


class Command(BaseCommand):
    help = "Seed the five level modules for level-based verification."

    def handle(self, *args, **options):
        created = 0
        for data in LEVEL_MODULES:
            obj, was_created = LevelModule.objects.get_or_create(
                level=data["level"],
                defaults=data,
            )
            if not was_created:
                for key, value in data.items():
                    setattr(obj, key, value)
                obj.save()
            created += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created} level modules (Levels 1-5)."
            )
        )

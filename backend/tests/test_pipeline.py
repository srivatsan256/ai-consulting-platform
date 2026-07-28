"""
Test script for the document extraction and rule engine pipeline.
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from verification.rule_engine import RuleEngine
from projects.models import Project, Document


def run_tests():
    print("1. Creating dummy project...")
    project = Project.objects.create(
        company_name="Acme Corp",
        industry="Fintech",
        project_name="AI Billing Integration",
        objectives="Build automated invoice matching with high accuracy.",
    )
    print(f"   Project created: {project.id}")

    print("2. Testing Rule Engine with sample BRD text...")
    sample_brd = """
    Executive Summary: Project Overview and Scope.
    Business Requirements: The system must support stakeholder management,
    defined objectives, assumptions, constraints, and acceptance criteria.
    Out of Scope: Manual entry.
    Glossary: Terms defined here.
    """
    engine = RuleEngine()
    result = engine.run(
        document_text=sample_brd,
        doc_type="BRD",
        use_ai=False,
        project_context=project.objectives,
    )
    print("   Rule engine output:", result)
    assert result["passed"] is True, "Sample BRD should pass verification"
    assert result["score"] >= 70.0, f"Expected score >= 70.0, got {result['score']}"

    print("3. Creating Document record...")
    doc = Document.objects.create(
        project=project,
        doc_type="BRD",
        extracted_text=sample_brd,
        verification_status=result["status"],
        missing_keywords=result["missing_keywords"],
        missing_sections=result["missing_sections"],
    )
    print(f"   Document saved: {doc.id}")

    # Clean up test data
    project.delete()
    print("4. Cleaned up test data. All pipeline tests passed! ✅")


if __name__ == "__main__":
    run_tests()

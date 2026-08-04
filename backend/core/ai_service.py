from __future__ import annotations

import os
from typing import Any


class _MockMessage:
    def __init__(self, content: str):
        self.content = content


class _MockChoice:
    def __init__(self, content: str):
        self.message = _MockMessage(content)


class _MockCompletionsResponse:
    def __init__(self, content: str):
        self.choices = [_MockChoice(content)]


class _MockCompletions:
    def create(self, **kwargs: Any) -> _MockCompletionsResponse:
        messages = kwargs.get("messages", [])
        return _MockCompletionsResponse(_build_mock_reply(messages))


class _MockChat:
    completions = _MockCompletions()


class _MockLLMClient:
    """Drops in for an OpenAI client so AI endpoints work without an API key."""

    chat = _MockChat()


def _build_mock_reply(messages: list) -> str:
    system_prompt = ""
    user_prompt = ""
    for message in messages:
        role = message.get("role", "")
        content = message.get("content", "")
        if role == "system":
            system_prompt += content
        elif role == "user":
            user_prompt = content

    if "technical writer" in system_prompt:
        return (
            "1. Executive Summary\n"
            "This document outlines the scope, objectives and delivery plan for "
            "the engagement.\n\n"
            "2. Objectives\n"
            "- Deliver measurable business value within the agreed timeline.\n"
            "- Establish a clear governance and change management framework.\n\n"
            "3. Approach\n"
            "We will run a structured discovery phase followed by iterative "
            "delivery sprints with continuous client feedback.\n\n"
            "4. Deliverables\n"
            "- Discovery report\n- Solution architecture\n- Implementation roadmap\n\n"
            "5. Timeline & Resources\n"
            "Delivery is planned over the agreed 3-month horizon with a dedicated "
            "cross-functional team.\n"
        )

    if "AI consulting expert" in system_prompt:
        return (
            "1. Churn Prediction Model - Build a machine learning model to identify "
            "customers at risk of churning within 90 days. Business value: retain "
            "15% more customers. Priority: high. Estimated ROI: 3.5x in 12 months. "
            "Timeline: 6 weeks.\n\n"
            "2. AI-Powered Retention Campaigns - Automate personalized retention "
            "offers based on churn risk scores. Business value: lift campaign "
            "conversion by 25%. Priority: medium. Estimated ROI: 2.0x in 6 months. "
            "Timeline: 4 weeks.\n\n"
            "3. Customer Feedback Sentiment Analysis - Analyze support tickets and "
            "surveys to surface churn drivers early. Business value: earlier "
            "detection of at-risk accounts. Priority: medium. Estimated ROI: 1.5x "
            "in 3 months. Timeline: 3 weeks.\n\n"
            "4. Executive Churn Dashboard - Provide leadership with a real-time view "
            "of churn risk and retention actions. Business value: faster, data-driven "
            "decisions. Priority: low. Estimated ROI: 1.2x in 2 months. Timeline: "
            "2 weeks.\n"
        )

    return (
        "Overall feasibility assessment: The project shows strong alignment with "
        "business objectives and clear value potential. Data readiness is moderate; "
        "the organization should focus on data governance and quality controls "
        "before full-scale model deployment.\n\n"
        "Recommended next steps:\n"
        "- Formalize data ownership and quality standards.\n"
        "- Run a pilot with a small, high-impact use case.\n"
        "- Define KPIs and an ROI measurement framework from day one.\n\n"
        "Feasibility score: 3 out of 5. Key risks: data availability, change "
        "management, and governance maturity.\n"
    )


def get_llm_client():
    """Return a real OpenAI client when OPENAI_API_KEY is set, otherwise a mock."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        from openai import OpenAI

        return OpenAI(api_key=api_key)
    return _MockLLMClient()


def analyze_proposal(discovery_text: str) -> dict:
    """Placeholder - implement with your custom LLM"""
    return {
        "analysis": "",
        "model": "custom",
        "tokens_used": 0,
    }


def generate_project_proposal(project_name: str, discovery_summary: str) -> dict:
    """Placeholder - implement with your custom LLM"""
    return {
        "proposal": "",
        "model": "custom",
        "tokens_used": 0,
    }


def generate_verification_report(document_text: str, rules: list) -> dict:
    """Placeholder - implement with your custom LLM"""
    return {
        "report": "",
        "model": "custom",
        "tokens_used": 0,
    }


def analyze_document(document_text: str) -> dict:
    """Placeholder - implement with your custom LLM"""
    return {
        "analysis": "",
        "model": "custom",
        "tokens_used": 0,
    }


def generate_ai_response(
    user_message: str,
    context: str = "",
    knowledge_base_context: str = "",
) -> str:
    """Placeholder - implement with your custom LLM"""
    if os.environ.get("OPENAI_API_KEY"):
        from openai import OpenAI

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI consulting assistant. Answer based on the "
                        "project and knowledge base context provided."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Project context:\n{context}\n\n"
                        f"Knowledge base:\n{knowledge_base_context}\n\n"
                        f"Question: {user_message}"
                    ),
                },
            ],
            temperature=0.4,
            max_tokens=500,
        )
        return response.choices[0].message.content or ""

    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI consulting assistant. Answer based on the project "
                "and knowledge base context provided."
            ),
        },
        {
            "role": "user",
            "content": f"Question: {user_message}",
        },
    ]
    return _build_mock_reply(messages)


def keyword_extraction(text: str) -> list:
    """Placeholder - implement with your custom LLM"""
    return []


def language_analysis(text: str) -> dict:
    """Placeholder - implement with your custom LLM"""
    return {}

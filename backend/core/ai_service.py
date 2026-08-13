from __future__ import annotations

import json
import os
import re
from typing import Any

# ---------------------------------------------------------------------------
# Provider configuration
# ---------------------------------------------------------------------------

AI_PROVIDER_DEFAULT = "gemini"
GEMINI_MODEL_DEFAULT = "gemini-2.0-flash"
OPENAI_MODEL_DEFAULT = "gpt-4o-mini"


def get_provider() -> str:
    """Name of the active AI provider, driven by the AI_PROVIDER env var."""
    return os.environ.get("AI_PROVIDER", AI_PROVIDER_DEFAULT).strip().lower()


def get_gemini_model() -> str:
    return os.environ.get("GEMINI_MODEL", GEMINI_MODEL_DEFAULT)


def get_gemini_api_key() -> str:
    return os.environ.get("GEMINI_API_KEY", "").strip()


def _gemini_generate(
    *,
    user_prompt: str,
    system_prompt: str = "",
    temperature: float = 0.4,
    max_tokens: int = 2000,
    response_format: dict | None = None,
) -> str:
    """Run a single Gemini generation and return the text response."""
    from google import genai
    from google.genai import types

    api_key = get_gemini_api_key()
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to the backend .env file."
        )

    client = genai.Client(api_key=api_key)
    config: dict[str, Any] = {
        "system_instruction": system_prompt,
        "temperature": temperature,
        "max_output_tokens": max_tokens,
    }
    if response_format:
        config["response_mime_type"] = "application/json"
    response = client.models.generate_content(
        model=get_gemini_model(),
        contents=user_prompt,
        config=types.GenerateContentConfig(**config),
    )
    return response.text or ""


def _extract_json(text: str) -> Any:
    """Best-effort extraction of a JSON value from a Gemini response."""
    if not text:
        return None
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            pass
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            pass
    return None


# ---------------------------------------------------------------------------
# OpenAI-compatible wrapper over Gemini
# ---------------------------------------------------------------------------

class _GeminiMessage:
    def __init__(self, content: str):
        self.content = content


class _GeminiChoice:
    def __init__(self, content: str):
        self.message = _GeminiMessage(content)


class _GeminiCompletionsResponse:
    def __init__(self, content: str):
        self.choices = [_GeminiChoice(content)]


class _GeminiCompletions:
    """OpenAI-shaped ``chat.completions.create`` backed by Google Gemini."""

    def create(self, **kwargs: Any) -> _GeminiCompletionsResponse:
        messages = kwargs.get("messages", [])
        system_prompt = ""
        user_prompt = ""
        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            if role == "system":
                system_prompt += content
            elif role == "user":
                user_prompt = content
        text = _gemini_generate(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=kwargs.get("temperature", 0.4),
            max_tokens=kwargs.get("max_tokens", 2000),
            response_format=kwargs.get("response_format"),
        )
        return _GeminiCompletionsResponse(text)


class _GeminiChat:
    completions = _GeminiCompletions()


class _GeminiClient:
    """Drops in for an OpenAI client, routing to Gemini instead."""

    chat = _GeminiChat()


# ---------------------------------------------------------------------------
# Mock fallback (used when no API key is configured)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Public client factory
# ---------------------------------------------------------------------------

def get_llm_client():
    """Return a real Gemini-backed client when GEMINI_API_KEY is set,
    otherwise fall back to the mock client."""
    provider = get_provider()
    if provider == "gemini" and get_gemini_api_key():
        return _GeminiClient()
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            from openai import OpenAI

            return OpenAI(api_key=api_key)
    return _MockLLMClient()


# ---------------------------------------------------------------------------
# Feature helpers (proposal, verification, documents, chatbot, keywords)
# ---------------------------------------------------------------------------

def analyze_proposal(discovery_text: str) -> dict:
    """Analyze a discovery text and return an LLM assessment."""
    text = _gemini_generate(
        user_prompt=(
            "You are an AI consulting analyst. Analyze the following discovery "
            "text and provide a structured assessment of feasibility, strengths, "
            "risks, recommended AI interventions, and an overall feasibility "
            "score.\n\n"
            f"Discovery text:\n{discovery_text}"
        ),
        system_prompt=(
            "You are an AI consulting analyst for an AI consulting platform. "
            "Provide clear, actionable analysis."
        ),
        temperature=0.3,
        max_tokens=2000,
    )
    return {
        "analysis": text,
        "model": f"gemini-{get_gemini_model()}",
        "tokens_used": 0,
    }


def generate_project_proposal(project_name: str, discovery_summary: str) -> dict:
    """Generate a professional project proposal with Gemini."""
    text = _gemini_generate(
        user_prompt=(
            "Generate a comprehensive project proposal for:\n"
            f"Project: {project_name}\n"
            f"Discovery Summary:\n{discovery_summary}\n\n"
            "Include: executive summary, project overview, objectives, timeline, "
            "resources, risks, and success metrics."
        ),
        system_prompt=(
            "You are an AI consulting platform that generates professional "
            "project proposals."
        ),
        temperature=0.4,
        max_tokens=3000,
    )
    return {
        "proposal": text,
        "model": f"gemini-{get_gemini_model()}",
        "tokens_used": 0,
    }


def generate_verification_report(document_text: str, rules: list) -> dict:
    """Verify a document against compliance rules with Gemini."""
    rules_text = "\n".join(f"- {rule}" for rule in rules) if rules else "- None provided"
    text = _gemini_generate(
        user_prompt=(
            "Verify this document against the following compliance rules and "
            "produce a verification report with per-rule PASS/FAIL, an overall "
            "compliance score, issues, and recommendations.\n\n"
            f"Rules:\n{rules_text}\n\n"
            f"Document:\n{document_text}"
        ),
        system_prompt=(
            "You are a document verification AI. Verify documents against "
            "compliance rules and generate structured reports."
        ),
        temperature=0.2,
        max_tokens=2000,
    )
    return {
        "report": text,
        "model": f"gemini-{get_gemini_model()}",
        "tokens_used": 0,
    }


def analyze_document(document_text: str) -> dict:
    """Analyze document content, structure and quality with Gemini."""
    text = _gemini_generate(
        user_prompt=(
            "Analyze this document and provide: document type classification, "
            "key sections, content quality assessment, completeness score (0-100), "
            "language analysis (tone, clarity), and suggested improvements.\n\n"
            f"Document:\n{document_text}"
        ),
        system_prompt=(
            "You are an AI document analyst. Analyze documents for content, "
            "structure, and quality."
        ),
        temperature=0.3,
        max_tokens=2000,
    )
    return {
        "analysis": text,
        "model": f"gemini-{get_gemini_model()}",
        "tokens_used": 0,
    }


def generate_ai_response(
    user_message: str,
    context: str = "",
    knowledge_base_context: str = "",
) -> str:
    """Generate an AI assistant reply (chatbot) with Gemini."""
    user_prompt = (
        f"Project context:\n{context}\n\n"
        f"Knowledge base:\n{knowledge_base_context}\n\n"
        f"Question: {user_message}"
    )
    return _gemini_generate(
        user_prompt=user_prompt,
        system_prompt=(
            "You are an AI assistant for an AI consulting platform. Help users "
            "with project-related questions, document analysis, and consulting "
            "guidance. Answer based on the project and knowledge base context "
            "provided."
        ),
        temperature=0.4,
        max_tokens=1500,
    )


def keyword_extraction(text: str) -> list:
    """Extract key technical and business keywords with Gemini."""
    raw = _gemini_generate(
        user_prompt=(
            "Extract key technical and business keywords from the following text. "
            'Return ONLY a JSON array of strings, e.g. ["keyword1", "keyword2"].\n\n'
            f"Text:\n{text}"
        ),
        system_prompt="You extract concise keyword lists and return JSON only.",
        temperature=0.1,
        max_tokens=500,
        response_format={"type": "json_object"},
    )
    data = _extract_json(raw)
    if isinstance(data, list):
        return [str(item) for item in data]
    return []


def language_analysis(text: str) -> dict:
    """Analyze document language quality with Gemini."""
    raw = _gemini_generate(
        user_prompt=(
            "Perform a language analysis on the following text. Return ONLY JSON "
            "with these keys: tone (string), clarity_score (1-10), "
            "reading_level (string), suggestions (array of strings).\n\n"
            f"Text:\n{text}"
        ),
        system_prompt="You perform language analysis and return JSON only.",
        temperature=0.2,
        max_tokens=500,
        response_format={"type": "json_object"},
    )
    data = _extract_json(raw)
    if isinstance(data, dict):
        return data
    return {}

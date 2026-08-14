from __future__ import annotations

import json
import os
import re
from typing import Any

from core.token_reduction import (
    distill,
    estimate_tokens,
    get_cache,
    make_cache_key,
    split_text,
)

# ---------------------------------------------------------------------------
# Provider configuration
# ---------------------------------------------------------------------------

AI_PROVIDER_DEFAULT = "gemini"
GEMINI_MODEL_DEFAULT = "gemini-2.0-flash"
OPENAI_MODEL_DEFAULT = "gpt-4o-mini"
AIRLLM_MODEL_DEFAULT = "Llama 3.1 8B Instruct"
AI_TOKEN_BUDGET_DEFAULT = 6000


def get_provider() -> str:
    """Name of the active AI provider, driven by the AI_PROVIDER env var."""
    return os.environ.get("AI_PROVIDER", AI_PROVIDER_DEFAULT).strip().lower()


def get_gemini_model() -> str:
    return os.environ.get("GEMINI_MODEL", GEMINI_MODEL_DEFAULT)


def get_gemini_api_key() -> str:
    return os.environ.get("GEMINI_API_KEY", "").strip()


def get_openai_model() -> str:
    return os.environ.get("OPENAI_MODEL", OPENAI_MODEL_DEFAULT)


def get_airllm_model() -> str:
    return os.environ.get("AIRLLM_MODEL", AIRLLM_MODEL_DEFAULT).strip()


def get_airllm_device() -> str:
    return os.environ.get("AIRLLM_DEVICE", "").strip() or None


def get_token_budget() -> int:
    """Maximum input tokens allowed per generation (all providers)."""
    return int(os.environ.get("AI_TOKEN_BUDGET", AI_TOKEN_BUDGET_DEFAULT))


def has_valid_gemini_key() -> bool:
    """True when a real Gemini API key is configured.

    Real Gemini keys start with ``AIza``. Empty values and placeholders
    (e.g. ``YOUR_GEMINI_API_KEY_HERE``) count as "not configured" so the
    service falls back to the mock client until a real key is provided.
    """
    key = get_gemini_api_key()
    return key.lower().startswith("aiza")


def has_valid_openai_key() -> bool:
    """True when a real OpenAI API key is configured.

    Real OpenAI keys start with ``sk-``. Empty values and placeholders
    (e.g. ``YOUR_OPENAI_API_KEY_HERE``) count as "not configured".
    """
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    return key.lower().startswith("sk-")


def is_airllm_configured() -> bool:
    """True when an AirLLM model name is configured.

    The airllm package itself is lazily imported on first generation and
    gracefully falls back to the mock client if unavailable.
    """
    return bool(get_airllm_model())


def get_model_name(provider: str | None = None) -> str:
    provider = (provider or get_provider()).strip().lower()
    if provider == "gemini":
        return get_gemini_model()
    if provider == "openai":
        return get_openai_model()
    if provider == "airllm":
        return get_airllm_model()
    return "mock"


# ---------------------------------------------------------------------------
# Unified generation gateway (token reduction + caching + provider routing)
# ---------------------------------------------------------------------------


def _build_chat_messages(system_prompt: str, user_prompt: str) -> list:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if user_prompt:
        messages.append({"role": "user", "content": user_prompt})
    return messages


def _reduce_prompts(
    system_prompt: str,
    user_prompt: str,
    budget: int,
    max_tokens: int,
) -> tuple:
    """Token reduction: keep total input tokens within budget.

    The output token allowance is reserved first, then the user prompt is
    truncated (and the system prompt as a last resort) so the full context
    stays inside the configured ``AI_TOKEN_BUDGET``.
    """
    output_allowance = min(max_tokens, budget // 2)
    input_budget = max(1, budget - output_allowance)

    system_tokens = estimate_tokens(system_prompt)
    user_tokens = estimate_tokens(user_prompt)

    if system_tokens + user_tokens <= input_budget:
        return system_prompt, user_prompt

    user_tokens = min(user_tokens, max(0, input_budget - system_tokens))
    user_prompt = distill(user_prompt, user_tokens) or truncate_to_budget(
        user_prompt, user_tokens
    )

    if estimate_tokens(system_prompt) + estimate_tokens(user_prompt) > input_budget:
        remaining = max(1, input_budget - estimate_tokens(user_prompt))
        system_prompt = truncate_to_budget(system_prompt, remaining)

    return system_prompt, user_prompt


def truncate_to_budget(text: str, max_tokens: int) -> str:
    """Truncate ``text`` to ``max_tokens`` (thin wrapper over token_reduction)."""
    from core.token_reduction import truncate

    return truncate(text, max_tokens)


def _dispatch(
    *,
    provider: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int,
    response_format: dict | None,
) -> str:
    """Route a generation to the active provider.

    Falls back to the deterministic mock reply when the provider is not
    configured (placeholder/missing keys, missing airllm package) so the
    platform never breaks during local development.
    """
    messages = _build_chat_messages(system_prompt, user_prompt)

    if provider == "gemini" and has_valid_gemini_key():
        return _gemini_raw_generate(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

    if provider == "openai" and has_valid_openai_key():
        return _openai_raw_generate(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    if provider == "airllm" and is_airllm_configured():
        try:
            return _airllm_raw_generate(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception:
            # Missing airllm package / model load failure -> mock fallback.
            return _build_mock_reply(messages)

    return _build_mock_reply(messages)


def _call_llm(
    *,
    user_prompt: str,
    system_prompt: str = "",
    temperature: float = 0.4,
    max_tokens: int = 2000,
    response_format: dict | None = None,
    provider: str | None = None,
) -> str:
    """Unified entry point: applies token reduction + caching, then routes.

    This is the single gateway every AI feature helper should use so token
    budgets and response caching apply across all providers.
    """
    provider = (provider or get_provider()).strip().lower()

    system_prompt, user_prompt = _reduce_prompts(
        system_prompt,
        user_prompt,
        get_token_budget(),
        max_tokens,
    )

    cache_key = make_cache_key(
        provider,
        get_model_name(provider),
        system_prompt,
        user_prompt,
        temperature,
        max_tokens,
        response_format,
    )
    cached = get_cache().get(cache_key)
    if cached is not None:
        return cached

    text = _dispatch(
        provider=provider,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format=response_format,
    )
    get_cache().set(cache_key, text)
    return text


# ---------------------------------------------------------------------------
# Raw provider implementations (no token reduction / caching / fallback)
# ---------------------------------------------------------------------------


def _gemini_raw_generate(
    *,
    user_prompt: str,
    system_prompt: str = "",
    temperature: float = 0.4,
    max_tokens: int = 2000,
    response_format: dict | None = None,
) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=get_gemini_api_key())
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


def _openai_raw_generate(
    *,
    user_prompt: str,
    system_prompt: str = "",
    temperature: float = 0.4,
    max_tokens: int = 2000,
) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    response = client.chat.completions.create(
        model=get_openai_model(),
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content or ""


_airllm_model_singleton = None
_airllm_model_singleton_name = None


def _get_airllm_singleton():
    """Load (once per process) and return the AirLLM model."""
    global _airllm_model_singleton, _airllm_model_singleton_name

    from airllm import AutoModel

    model_name = get_airllm_model()
    if _airllm_model_singleton is not None and _airllm_model_singleton_name == model_name:
        return _airllm_model_singleton

    kwargs: dict[str, Any] = {}
    device = get_airllm_device()
    if device:
        kwargs["device"] = device
    _airllm_model_singleton = AutoModel.from_pretrained(model_name, **kwargs)
    _airllm_model_singleton_name = model_name
    return _airllm_model_singleton


def _airllm_raw_generate(
    *,
    user_prompt: str,
    system_prompt: str = "",
    temperature: float = 0.4,
    max_tokens: int = 512,
) -> str:
    model = _get_airllm_singleton()
    prompt = f"{system_prompt}\n\n{user_prompt}".strip()
    encoded = model.tokenizer(prompt, return_tensors="pt")
    output = model.generate(
        encoded.input_ids,
        max_new_tokens=max_tokens,
        temperature=temperature,
        do_sample=temperature > 0,
    )
    return model.tokenizer.decode(output[0], skip_special_tokens=True)



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
        text = _call_llm(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=kwargs.get("temperature", 0.4),
            max_tokens=kwargs.get("max_tokens", 2000),
            response_format=kwargs.get("response_format"),
            provider="gemini",
        )
        return _GeminiCompletionsResponse(text)


class _GeminiChat:
    completions = _GeminiCompletions()


class _GeminiClient:
    """Drops in for an OpenAI client, routing to Gemini instead."""

    chat = _GeminiChat()


# ---------------------------------------------------------------------------
# AirLLM client (local inference via layer-wise offloading)
# ---------------------------------------------------------------------------


class _AirLLMCompletionsResponse:
    def __init__(self, content: str):
        self.choices = [_GeminiChoice(content)]


class _AirLLMCompletions:
    """OpenAI-shaped ``chat.completions.create`` backed by AirLLM."""

    def create(self, **kwargs: Any) -> _AirLLMCompletionsResponse:
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
        text = _call_llm(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=kwargs.get("temperature", 0.4),
            max_tokens=kwargs.get("max_tokens", 512),
            provider="airllm",
        )
        return _AirLLMCompletionsResponse(text)


class _AirLLMChat:
    completions = _AirLLMCompletions()


class _AirLLMClient:
    """Drops in for an OpenAI client, routing to local AirLLM inference."""

    chat = _AirLLMChat()


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
    """Return a real provider-backed client when configured,
    otherwise fall back to the mock client."""
    provider = get_provider()
    if provider == "gemini" and has_valid_gemini_key():
        return _GeminiClient()
    if provider == "openai" and has_valid_openai_key():
        from openai import OpenAI

        return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    if provider == "airllm" and is_airllm_configured():
        return _AirLLMClient()
    return _MockLLMClient()


# ---------------------------------------------------------------------------
# Feature helpers (proposal, verification, documents, chatbot, keywords)
# ---------------------------------------------------------------------------

def _distill_input(text: str) -> str:
    """Distill a long document/context to a safe share of the token budget.

    Preserves the most important content (headings, numbers, business
    keywords) instead of blind truncation. ``_call_llm`` applies a final
    hard budget on top, so this only reduces what reaches the provider.
    """
    if not text:
        return text
    target = max(512, get_token_budget() // 4)
    return distill(text, target)


_DOCUMENT_ANALYSIS_PROMPT = (
    "Analyze this document and provide: document type classification, "
    "key sections, content quality assessment, completeness score (0-100), "
    "language analysis (tone, clarity), and suggested improvements.\n\n"
)


def analyze_document(document_text: str) -> dict:
    """Analyze document content, structure and quality.

    Chunks documents that exceed the token budget, analyzes each chunk
    independently, and merges the per-chunk analyses into one report.
    """
    if estimate_tokens(document_text) > get_token_budget():
        sections = split_text(
            document_text,
            chunk_tokens=max(1024, get_token_budget() // 3),
            overlap_tokens=128,
        )
        analyses = []
        for index, section in enumerate(sections, start=1):
            section_result = _call_llm(
                user_prompt=_DOCUMENT_ANALYSIS_PROMPT + f"Document:\n{section}",
                system_prompt=(
                    "You are an AI document analyst. Analyze documents for "
                    "content, structure, and quality."
                ),
                temperature=0.3,
                max_tokens=1200,
            )
            analyses.append(f"## Section {index}\n{section_result}")
        text = "\n\n".join(analyses)
    else:
        text = _call_llm(
            user_prompt=_DOCUMENT_ANALYSIS_PROMPT + f"Document:\n{document_text}",
            system_prompt=(
                "You are an AI document analyst. Analyze documents for "
                "content, structure, and quality."
            ),
            temperature=0.3,
            max_tokens=2000,
        )
    return {
        "analysis": text,
        "model": get_model_name(),
        "tokens_used": 0,
    }


def analyze_proposal(discovery_text: str) -> dict:
    """Analyze a discovery text and return an LLM assessment."""
    text = _call_llm(
        user_prompt=(
            "You are an AI consulting analyst. Analyze the following discovery "
            "text and provide a structured assessment of feasibility, strengths, "
            "risks, recommended AI interventions, and an overall feasibility "
            "score.\n\n"
            f"Discovery text:\n{_distill_input(discovery_text)}"
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
        "model": get_model_name(),
        "tokens_used": 0,
    }


def generate_project_proposal(project_name: str, discovery_summary: str) -> dict:
    """Generate a professional project proposal."""
    text = _call_llm(
        user_prompt=(
            "Generate a comprehensive project proposal for:\n"
            f"Project: {project_name}\n"
            f"Discovery Summary:\n{_distill_input(discovery_summary)}\n\n"
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
        "model": get_model_name(),
        "tokens_used": 0,
    }


def generate_verification_report(document_text: str, rules: list) -> dict:
    """Verify a document against compliance rules."""
    rules_text = "\n".join(f"- {rule}" for rule in rules) if rules else "- None provided"
    text = _call_llm(
        user_prompt=(
            "Verify this document against the following compliance rules and "
            "produce a verification report with per-rule PASS/FAIL, an overall "
            "compliance score, issues, and recommendations.\n\n"
            f"Rules:\n{rules_text}\n\n"
            f"Document:\n{_distill_input(document_text)}"
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
        "model": get_model_name(),
        "tokens_used": 0,
    }


def generate_ai_response(
    user_message: str,
    context: str = "",
    knowledge_base_context: str = "",
) -> str:
    """Generate an AI assistant reply (chatbot)."""
    user_prompt = (
        f"Project context:\n{_distill_input(context)}\n\n"
        f"Knowledge base:\n{_distill_input(knowledge_base_context)}\n\n"
        f"Question: {user_message}"
    )
    return _call_llm(
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
    """Extract key technical and business keywords."""
    raw = _call_llm(
        user_prompt=(
            "Extract key technical and business keywords from the following text. "
            'Return ONLY a JSON array of strings, e.g. ["keyword1", "keyword2"].\n\n'
            f"Text:\n{_distill_input(text)}"
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
    """Analyze document language quality."""
    raw = _call_llm(
        user_prompt=(
            "Perform a language analysis on the following text. Return ONLY JSON "
            "with these keys: tone (string), clarity_score (1-10), "
            "reading_level (string), suggestions (array of strings).\n\n"
            f"Text:\n{_distill_input(text)}"
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

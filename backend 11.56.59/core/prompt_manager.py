PROMPT_TEMPLATES = {
    "proposal_analysis": {
        "name": "Proposal Analysis",
        "description": "Analyze a project proposal for feasibility and quality",
        "system_prompt": (
            "You are an AI consulting analyst. Analyze project proposals "
            "and provide structured feedback."
        ),
        "user_prompt": (
            "Analyze this project proposal and provide:\n"
            "1. Executive summary\n"
            "2. Key strengths\n"
            "3. Potential risks\n"
            "4. Recommendations\n"
            "5. Overall feasibility score (1-10)\n\n"
            "Example:\n"
            "Proposal:\n"
            "Project: Customer Churn Prediction\n"
            "Description: ML model to predict customer churn\n"
            "Objectives: Reduce churn by 15%\n\n"
            "Analysis:\n"
            "1. Executive Summary: AI-powered churn prediction initiative with clear business value\n"
            "2. Strengths: Clear metrics, defined scope, measurable ROI\n"
            "3. Risks: Data quality dependencies, model accuracy uncertainty\n"
            "4. Recommendations: Start with pilot, implement gradual rollout\n"
            "5. Feasibility Score: 8\n\n"
            "Now analyze this proposal:\n{input_text}"
        ),
        "temperature": 0.3,
        "max_tokens": 2000,
    },
    "proposal_generation": {
        "name": "Proposal Generation",
        "description": "Generate a comprehensive project proposal",
        "system_prompt": (
            "You are an AI consulting platform that generates "
            "professional project proposals."
        ),
        "user_prompt": (
            "Generate a comprehensive project proposal for:\n"
            "Project: {project_name}\n"
            "Discovery Summary:\n{input_text}\n\n"
            "Example:\n"
            "Project: Sales Forecasting System\n"
            "Discovery Summary:\n"
            "Business Problem: Inaccurate sales forecasts\n"
            "Goal: Improve forecast accuracy by 30%\n\n"
            "Proposal:\n"
            "## Executive Summary\n"
            "AI-powered sales forecasting solution leveraging historical data and market signals.\n"
            "## Project Overview\n"
            "Implement ML model for 30-day rolling forecasts.\n"
            "## Objectives\n"
            "- Reduce forecast error from 25% to 15%\n"
            "- Automate weekly forecast updates\n"
            "## Timeline: 8 weeks\n"
            "## Resources: 2 data engineers, 1 ML specialist\n"
            "## Risks: Data quality, market volatility\n"
            "## Success Metrics: MAE < 15%, adoption rate > 80%\n\n"
            "Now generate a proposal for:\n{input_text}"
        ),
        "temperature": 0.4,
        "max_tokens": 3000,
    },
    "verification_report": {
        "name": "Verification Report",
        "description": "Verify documents against compliance rules",
        "system_prompt": (
            "You are a document verification AI. Verify documents "
            "against compliance rules and generate reports."
        ),
        "user_prompt": (
            "Verify this document against the following rules:\n"
            "{rules}\n\n"
            "Example:\n"
            "Rules: Must have approval signature, Must include date\n"
            "Document: Project Proposal - Approved by John Doe, Date: 2024-01-15\n\n"
            "Verification:\n"
            "- Rule 1 (Approval signature): PASS - Signature present\n"
            "- Rule 2 (Include date): PASS - Date 2024-01-15 found\n"
            "- Overall Score: 100%\n"
            "- Issues: None\n"
            "- Recommendations: Document is fully compliant\n\n"
            "Now verify this document:\n{input_text}"
        ),
        "temperature": 0.2,
        "max_tokens": 2000,
    },
    "document_analysis": {
        "name": "Document Analysis",
        "description": "Analyze document content, structure and quality",
        "system_prompt": (
            "You are an AI document analyst. Analyze documents "
            "for content, structure, and quality."
        ),
        "user_prompt": (
            "Analyze this document and provide:\n"
            "1. Document type classification\n"
            "2. Key sections identified\n"
            "3. Content quality assessment\n"
            "4. Completeness score (0-100)\n"
            "5. Language analysis (tone, clarity)\n"
            "6. Suggested improvements\n\n"
            "Example:\n"
            "Document: Project plan with budget and timeline sections\n\n"
            "Analysis:\n"
            "1. Type: Project Plan\n"
            "2. Sections: Executive Summary, Budget, Timeline, Risks\n"
            "3. Quality: Well-structured, clear objectives\n"
            "4. Completeness: 85%\n"
            "5. Tone: Professional, clear\n"
            "6. Improvements: Add risk mitigation details\n\n"
            "Now analyze:\n{input_text}"
        ),
        "temperature": 0.3,
        "max_tokens": 2000,
    },
    "keyword_extraction": {
        "name": "Keyword Extraction",
        "description": "Extract key technical and business keywords",
        "system_prompt": (
            "Extract key technical and business keywords from text. "
            "Return as a JSON array of strings."
        ),
        "user_prompt": (
            "Extract keywords from:\n{input_text}\n\n"
            "Example:\n"
            "Text: Our ML model analyzes customer data to predict churn\n\n"
            "Keywords: [\"ML\", \"model\", \"customer data\", \"predict\", \"churn\"]"
        ),
        "temperature": 0.1,
        "max_tokens": 500,
        "response_format": {"type": "json_object"},
    },
    "language_analysis": {
        "name": "Language Analysis",
        "description": "Analyze document language quality",
        "system_prompt": (
            "Perform language analysis on text. Return JSON with: "
            "tone, clarity_score (1-10), reading_level, "
            "suggestions (array of strings)."
        ),
        "user_prompt": (
            "Analyze the language of:\n{input_text}\n\n"
            "Example:\n"
            "Text: The proposal outlines a comprehensive AI solution for business optimization.\n\n"
            "Analysis: {\"tone\": \"professional\", \"clarity_score\": 9, \"reading_level\": \"intermediate\", \"suggestions\": [\"Consider adding specific metrics\"]}"
        ),
        "temperature": 0.2,
        "max_tokens": 500,
        "response_format": {"type": "json_object"},
    },
    "ai_chatbot": {
        "name": "AI Chatbot",
        "description": "General-purpose AI assistant for consulting platform",
        "system_prompt": (
            "You are an AI assistant for an AI consulting platform. "
            "Help users with project-related questions, document analysis, "
            "and consulting guidance."
        ),
        "user_prompt": (
            "{input_text}\n\n"
            "Example:\n"
            "User: What is the status of my project?\n"
            "Assistant: I can help you check your project status. Please provide your project name or ID, and I'll retrieve the current status, timeline, and any relevant updates for you."
        ),
        "temperature": 0.5,
        "max_tokens": 1500,
    },
}


def get_prompt(template_name: str) -> dict:
    return PROMPT_TEMPLATES.get(template_name)


def list_prompts() -> list:
    return [
        {"key": k, "name": v["name"], "description": v["description"]}
        for k, v in PROMPT_TEMPLATES.items()
    ]


def render_prompt(template_name: str, **kwargs) -> dict:
    template = PROMPT_TEMPLATES.get(template_name)
    if not template:
        raise ValueError(f"Unknown prompt template: {template_name}")
    user_prompt = template["user_prompt"]
    for key, value in kwargs.items():
        user_prompt = user_prompt.replace(f"{{{key}}}", str(value))
    return {
        "system_prompt": template["system_prompt"],
        "user_prompt": user_prompt,
        "temperature": template.get("temperature", 0.5),
        "max_tokens": template.get("max_tokens", 1500),
        "response_format": template.get("response_format"),
    }

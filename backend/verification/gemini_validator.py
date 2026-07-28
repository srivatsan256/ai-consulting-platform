import logging
from django.conf import settings
import google.generativeai as genai

logger = logging.getLogger(__name__)

def gemini_validate(
    document_text: str,
    doc_type: str,
    missing_keywords: list,
    missing_sections: list,
    project_context: str = "",
) -> str:
    """Run Gemini AI qualitative document validation.

    Args:
        document_text: Full extracted text of the document.
        doc_type: Document type (e.g., 'BRD', 'FRD').
        missing_keywords: List of keywords the rule engine flagged as missing.
        missing_sections: List of sections the rule engine flagged as missing.
        project_context: Optional brief description of the project.

    Returns:
        A concise feedback string (≤150 words) summarising quality, gaps and recommendations.
    """
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")
        snippet = document_text[:3000]
        prompt = f"""
You are a senior business analyst reviewing a {doc_type} document.

Project Context:
{project_context or "Not provided"}

Rule Engine Findings:

Missing Keywords:
{missing_keywords}

Missing Sections:
{missing_sections}

Document Content:
{snippet}

Analyze this document and provide:
1. Overall quality assessment
2. Critical missing information
3. Business risks
4. Recommended improvements

Keep the response under 150 words.
"""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as exc:
        logger.error("Gemini validation failed: %s", exc)
        return "AI analysis unavailable"

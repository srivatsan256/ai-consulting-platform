import google.generativeai as genai

from django.conf import settings
import os

_API_KEY = os.getenv('GEMINI_API_KEY')
if _API_KEY:
    genai.configure(api_key=_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_document(text: str, doc_type: str, project_context: str = "") -> dict:
    if not _API_KEY:
        return {"error": "GEMINI_API_KEY is not configured", "raw": "Gemini AI disabled"}

    prompt = f"""
    You are an expert business analyst.
    Analyze the following {doc_type} document for a project: {project_context}

    Document Content:
    {text[:15000]}  # truncate if too long

    Return JSON with:
    - completeness_score (0-100)
    - missing_keywords (list)
    - missing_sections (list)
    - recommendations (list)
    - overall_assessment (string)
    """
    response = model.generate_content(prompt)
    # Parse JSON response
    try:
        import json
        return json.loads(response.text)
    except:
        return {"error": "Failed to parse AI response", "raw": response.text}

"""
services/gemini_service.py
Gemini AI service integration for document consulting, RAG Q&A, and deliverable generation.
"""
import logging
from typing import List, Dict, Any, Optional
from django.conf import settings  # type: ignore

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self):
        self.api_key = getattr(settings, "GEMINI_API_KEY", None)

    def _get_model(self, model_name: str = "gemini-1.5-flash"):
        import google.generativeai as genai
        if not self.api_key:
            return None
        genai.configure(api_key=self.api_key)
        return genai.GenerativeModel(model_name)

    def ask_document_chat(
        self,
        question: str,
        documents: List[Dict[str, str]],
        project_context: str = "",
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        RAG Q&A over project documents using Gemini.
        """
        try:
            model = self._get_model("gemini-1.5-flash")
            if model is None:
                return "Gemini AI is not configured. Document chat is unavailable."
            
            # Combine document excerpts into context
            doc_context = ""
            for doc in documents:
                snippet = (doc.get("text") or "")[:4000]
                doc_type = doc.get("doc_type", "Document")
                doc_context += f"\n--- {doc_type} Excerpt ---\n{snippet}\n"

            prompt = f"""
You are an expert AI Business Analyst & Management Consultant.

Project Context & Objectives:
{project_context or "N/A"}

Project Uploaded Documents:
{doc_context or "No documents uploaded yet."}

User Question:
{question}

Answer clearly with structured sections, bullet points, and actionable recommendations based strictly on the provided project documents.
"""
            response = model.generate_content(prompt)
            return response.text.strip()

        except Exception as exc:
            logger.error("Gemini Q&A failed: %s", exc)
            return f"Error connecting to Gemini AI: {exc}"

    def generate_deliverable(
        self,
        deliverable_type: str,
        project_info: Dict[str, Any],
        documents: List[Dict[str, str]],
    ) -> str:
        """
        Generate standardized BRD, FRD, or PRD content based on project details and uploaded documents.
        """
        try:
            model = self._get_model("gemini-1.5-pro")
            if model is None:
                return f"# {deliverable_type} - {project_info.get('project_name')}\n\n*Gemini AI is not configured. Generated placeholder content.*"
            
            doc_text = "\n\n".join(
                [f"[{d.get('doc_type', 'Doc')}]: {(d.get('text') or '')[:3000]}" for d in documents]
            )

            prompt = f"""
Generates a comprehensive, professional {deliverable_type} document in Markdown format.

Company: {project_info.get('company_name')}
Project Name: {project_info.get('project_name')}
Industry: {project_info.get('industry')}
Objectives: {project_info.get('objectives')}
Team Members: {project_info.get('team_members')}
Timeline: {project_info.get('expected_timeline')}

Source Documents Provided:
{doc_text or "None"}

Requirements for the generated document:
1. Executive Summary & Purpose
2. Scope & Key Objectives
3. Functional & Technical Requirements
4. System Architecture & Workflows
5. Risk Assessment & Mitigations
6. Approval & Sign-off Table

Generate the full, publication-ready document in valid GitHub Markdown.
"""
            response = model.generate_content(prompt)
            return response.text.strip()

        except Exception as exc:
            logger.error("Gemini deliverable generation failed: %s", exc)
            return f"# {deliverable_type} - {project_info.get('project_name')}\n\n*Generated placeholder due to AI connection issue: {exc}*"

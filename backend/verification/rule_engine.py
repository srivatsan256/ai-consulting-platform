from .level_verifier import verify_level_document

class RuleEngine:
    def run(self, document_text, doc_type=None, use_ai=False, project_context="", level=1):
        return self.run_verification(document_text=document_text, level=level)

    def run_verification(self, document_text, level=1, doc_type=None):
        return verify_level_document(document_text=document_text or "", level=level)

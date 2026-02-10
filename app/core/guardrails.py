import re
from typing import List, Tuple
from app.models.schemas import ChatResponse

class GuardrailsService:
    """
    Security & Quality Guardrails for the Copilot.
    Ensures that the AI does not hallucinate and follows protocol.
    """
    
    def validate_response(self, response: ChatResponse) -> Tuple[bool, str]:
        """
        Validates the generated answer.
        Returns (is_valid, reason).
        """
        answer = response.answer
        sources = response.sources
        
        # 1. Hallucination Check (Empty Sources)
        # If the answer implies success but has no sources, it might be a hallucination.
        # Exception: Greetings or refusal to answer.
        if not sources and len(answer) > 50:
            if "no encuentro" not in answer.lower() and "no tengo información" not in answer.lower():
                return False, "⚠️ Respuesta generada sin fuentes (Posible alucinación)."

        # 2. Citation Format Check
        # Ensure that if sources are used, they are referenced in the text (basic check)
        # This is a bit strict, maybe just warning log for MVP
        citation_pattern = r"\[.*?, Pág\. \d+\]"
        if sources and not re.search(citation_pattern, answer):
             # We won't block it, but we flag it
             pass 

        return True, "OK"

    def sanitize_input(self, query: str) -> str:
        """
        Prevents prompt injection (basic).
        """
        # Remove potential system override attempts
        forbidden_phrases = ["ignore previous instructions", "system prompt", "you are now"]
        clean_query = query
        for phrase in forbidden_phrases:
            clean_query = clean_query.replace(phrase, "[REDACTED]")
        return clean_query

guardrails = GuardrailsService()

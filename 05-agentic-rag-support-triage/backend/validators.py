class ValidationService:
    @staticmethod
    def check_grounding(answer: str, context: list) -> bool:
        """Checks if the answer contains key terms from the context."""
        if not context or not answer:
            return False
        
        # Simple heuristic: Check if significant words from context appear in answer
        context_words = set(" ".join(context).lower().split())
        answer_words = set(answer.lower().split())
        
        intersection = context_words.intersection(answer_words)
        # If less than 20% overlap, it might be hallucinated
        overlap_ratio = len(intersection) / len(context_words) if context_words else 0
        
        return overlap_ratio > 0.2

    @staticmethod
    def check_safety(answer: str) -> bool:
        """Basic safety check for PII or harmful content."""
        forbidden_terms = ["password", "credit card", "ssn", "private key"]
        return not any(term in answer.lower() for term in forbidden_terms)

validation_service = ValidationService()
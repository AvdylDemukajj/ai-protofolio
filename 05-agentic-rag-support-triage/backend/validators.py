"""Answer validation (grounding and safety)."""


class ValidationService:
    @staticmethod
    def check_grounding(answer: str, context: list[str]) -> bool:
        if not context or not answer:
            return False
        context_words = {w for w in " ".join(context).lower().split() if len(w) > 3}
        answer_words = set(answer.lower().split())
        if not context_words:
            return True
        overlap = len(context_words.intersection(answer_words)) / len(context_words)
        return overlap > 0.15

    @staticmethod
    def check_safety(answer: str) -> bool:
        forbidden = ["password", "credit card", "ssn", "private key", "social security"]
        lowered = answer.lower()
        return not any(term in lowered for term in forbidden)


validation_service = ValidationService()

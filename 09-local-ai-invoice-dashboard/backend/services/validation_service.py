from decimal import Decimal
from typing import Dict, Any

class ValidationService:
    def validate_math(self, data: Dict[str, Any]) -> bool:
        """Checks if Subtotal + Tax = Total."""
        try:
            subtotal = Decimal(str(data.get('subtotal', 0)))
            tax = Decimal(str(data.get('tax', 0)))
            total = Decimal(str(data.get('total', 0)))
            
            return abs((subtotal + tax) - total) < Decimal('0.05') # Allow small rounding diff
        except Exception:
            return False

    def determine_status(self, data: Dict[str, Any], math_valid: bool, threshold: float = 0.8) -> str:
        """Status from math validation and confidence."""
        if not math_valid:
            return "needs_review"
        confidence = float(data.get("confidence", 0))
        if confidence < threshold:
            return "needs_review"
        return "extracted"

validation_service = ValidationService()
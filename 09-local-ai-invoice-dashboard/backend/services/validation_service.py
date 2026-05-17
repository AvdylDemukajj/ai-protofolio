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

    def check_confidence(self, data: Dict[str, Any], threshold: float = 0.8) -> str:
        """Determines status based on confidence score."""
        confidence = float(data.get('confidence', 0))
        if confidence >= threshold:
            return "extracted" # Auto-approved for review queue
        return "needs_review" # Requires manual check

validation_service = ValidationService()
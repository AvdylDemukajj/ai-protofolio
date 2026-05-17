from backend.models import InvoiceData
from decimal import Decimal, ROUND_HALF_UP

class ValidationService:
    def validate_math(self, data: InvoiceData) -> bool:
        """Ensures Subtotal + Tax = Total (within small tolerance)."""
        subtotal = Decimal(str(data.subtotal))
        tax = Decimal(str(data.tax))
        total = Decimal(str(data.total))
        
        calculated_total = (subtotal + tax).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Allow 0.01 tolerance for rounding differences
        return abs(calculated_total - total) <= Decimal('0.01')

    def determine_status(self, data: InvoiceData, math_valid: bool) -> str:
        """Determines if human review is needed."""
        if not math_valid:
            return "needs_review"
        if data.confidence < 0.85:
            return "needs_review"
        if data.total > 10000: # High value threshold
            return "needs_review"
        return "processed" # Auto-approved for low risk

validation_service = ValidationService()
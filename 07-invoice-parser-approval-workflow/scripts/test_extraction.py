import sys
sys.path.append('..')
from backend.services.validation_service import ValidationService
from backend.models import InvoiceData

def test_math_validation():
    validator = ValidationService()
    
    # Valid Case
    data_valid = InvoiceData(vendor="A", invoice_number="1", invoice_date="2023-01-01", subtotal=100.0, tax=20.0, total=120.0, confidence=0.9)
    assert validator.validate_math(data_valid) == True
    
    # Invalid Case
    data_invalid = InvoiceData(vendor="B", invoice_number="2", invoice_date="2023-01-01", subtotal=100.0, tax=20.0, total=150.0, confidence=0.9)
    assert validator.validate_math(data_invalid) == False
    
    print("✅ Math Validation Tests Passed!")

if __name__ == "__main__":
    test_math_validation()
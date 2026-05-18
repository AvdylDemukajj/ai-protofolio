from billing_engine.invoice_generator import generate_monthly_invoice
from billing_engine.usage_tracker import log_usage

def test_billing_calculation():
    # Mock a tenant ID
    tenant_id = "00000000-0000-0000-0000-000000000000"
    
    # Log some usage
    log_usage(tenant_id, 'api_call', 1000)
    log_usage(tenant_id, 'storage_mb', 100)
    
    # Generate Invoice
    result = generate_monthly_invoice(tenant_id, 2023, 10)
    
    # Verify Calculation (Free plan = 0 base + usage)
    # 1000 calls * 0.001 = 1.0
    # 100 MB * 0.05 = 5.0
    # Total = 6.0
    assert result['total'] == 6.0
    print("✅ Billing Test Passed")
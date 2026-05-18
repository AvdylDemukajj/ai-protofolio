# Billing Logic

## Model: Hybrid (Subscription + Usage)
Total Cost = Base Plan Fee + (Usage Units * Unit Price)

## Tiers
- **Free**: $0/mo + $0.001/call.
- **Pro**: $29/mo (includes 10k calls) + $0.0005/extra call.
- **Enterprise**: Custom pricing.

## Implementation
- Usage events are logged asynchronously to `global_usage_logs` to avoid impacting API latency.
- Invoicing is a batch job run monthly (simulated in `invoice_generator.py`).
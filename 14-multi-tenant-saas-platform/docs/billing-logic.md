# Billing Logic

## Model: Hybrid (Subscription + Usage)

**Total cost** = base plan fee + metered overage (API calls beyond included quota, storage).

## Tiers

| Plan | Base fee | Included API calls | Overage per call | Storage |
|------|----------|-------------------|------------------|---------|
| Free | $0/mo | 0 | $0.001 | $0.05/MB |
| Pro | $29/mo | 10,000 | $0.0005 | $0.05/MB |
| Enterprise | $99/mo | 100,000 | $0.0003 | $0.05/MB |

## Implementation

- Usage events are written to `global_usage_logs` via `usage_tracker.py` (sync insert; production would use async queue).
- Invoicing is implemented in `billing_engine/invoice_generator.py` and can be run as a monthly batch job.
- Pro/Enterprise plans include a bundled API call quota; only usage above the quota is billed at the overage rate.

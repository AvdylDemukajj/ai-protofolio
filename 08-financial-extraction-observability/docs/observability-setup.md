# Observability Setup

## Metrics Collected
- `doc_processing_total`: Numri i dokumenteve të përpunuara (success/failure).
- `doc_processing_seconds`: Koha e nevojshme për OCR dhe ekstraktim.
- `queue_size`: Numri i dokumenteve në pritje.

## Alerts (Configurable in Grafana)
- If `queue_size` > 100 for 5 mins -> Scale up workers.
- If `rate(doc_processing_total{status="failed"})` > 10% -> Notify Engineering.
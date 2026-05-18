# Architecture

## Components

| Layer | Component | Responsibility |
|-------|-----------|----------------|
| Ingestion | n8n Webhook | Secured HTTP intake for support tickets |
| Ingestion | n8n Manual + CSV | Local demo batch processing |
| Processing | OpenAI (gpt-4o-mini) | Category, priority, confidence, summary |
| Processing | Code nodes | Validation, business rules, hashing |
| Persistence | PostgreSQL | `support_tickets`, `audit_logs` |
| Notification | Slack Incoming Webhook | High-priority alerts only |
| Edge (optional) | nginx | Rate limiting on `/webhook/` paths |

## Production data flow

```
External system
  → POST /webhook/support-intake + X-Webhook-Secret
  → Validate payload
  → INSERT support_tickets (status=new, source=webhook)
  → OpenAI classification (JSON)
  → Business rules (keywords, confidence)
  → UPDATE support_tickets (status=classified)
  → INSERT audit_logs (classification)
  → IF high priority AND confidence≥0.6 → Slack
  → HTTP 200 { ticket_id, priority, category }
```

## Demo data flow

```
Manual trigger (workflow 02)
  → Read demo-data/support_emails.csv
  → Same AI + DB + audit pipeline
  → source=csv_demo
```

## Security measures

- Isolated Docker network (`n8n-network`)
- Basic Auth on n8n UI
- Webhook shared secret header
- Optional nginx rate limiting (`docker compose --profile production`)
- Credential store for OpenAI and Postgres (no secrets in workflow JSON)
- Audit logs store SHA-256 input hashes

## Workflows

| File | Purpose |
|------|---------|
| `01_support_webhook_intake.json` | Production webhook pipeline |
| `02_demo_csv_batch.json` | Local CSV demo (inactive in prod) |
| `03_error_handler.json` | Global error logging and ops alert |

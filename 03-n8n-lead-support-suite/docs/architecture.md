# Architecture

## System context

Project 3 sits in the portfolio **lead lifecycle** track:

- **Project 1** — support ticket automation (port 5678)
- **Project 2** — pre-import security scanner
- **Project 3** — B2B lead intake, validation, AI scoring (port 5679)

## Components

```text
                    ┌─────────────┐
  Website / CRM ──► │   Webhook   │──┐
                    └─────────────┘  │
  CSV demo ───────► │ Manual CSV  │──┼──► PostgreSQL (leads)
                    └─────────────┘  │         │
                                       │         ▼
                    ┌─────────────┐  │    ┌──────────────┐
  Schedule 15m ───► │ Validation  │──┘    │ lead_audit   │
                    └─────────────┘       └──────────────┘
                           │
                           ▼
                    ┌─────────────┐
  Schedule 15m ───► │ AI Scoring  │──► Slack (hot leads)
                    └─────────────┘
```

## Technology choices

| Choice | Rationale |
|--------|-----------|
| n8n | Visual ops-friendly automation, portfolio consistency |
| Shared Postgres | App tables + n8n metadata in `leads_db` |
| OpenAI JSON scoring | Structured output for routing rules |
| Webhook secret | Simple production auth without HMAC complexity |
| Scheduled validation/scoring | Decouples ingest spikes from AI cost |

## Failure handling

- Per-workflow error handler writes audit row + Slack ops message
- AI parse failures degrade to safe defaults, not workflow crash
- Low-confidence leads flagged for human review instead of auto-Slack

## Security boundaries

- n8n UI behind Basic Auth
- Webhook authenticated via header secret
- Optional nginx rate limit (`docker compose --profile production`)
- No secrets in exported workflow JSON (credentials + `$env`)

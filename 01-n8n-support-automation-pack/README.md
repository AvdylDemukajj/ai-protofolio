# Project 1: n8n Support & Email Automation Pack

**Status:** Production-ready | Secured webhooks | OpenAI classification | Audit trail

Enterprise-style customer support automation: classify inbound tickets with AI, persist data in PostgreSQL with audit logs, and alert Slack for high-priority cases.

## Architecture

- **n8n** — workflow engine (webhook intake, AI, routing)
- **PostgreSQL** — `support_tickets` and `audit_logs`
- **OpenAI** — `gpt-4o-mini` classification
- **Slack** — high-priority notifications only
- **nginx** (optional) — rate limiting on webhook paths

See [docs/architecture.md](docs/architecture.md) for the full data flow.

## Quick start

### 1. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set strong values for:

- `N8N_ENCRYPTION_KEY` (32+ characters)
- `N8N_BASIC_AUTH_USER` / `N8N_BASIC_AUTH_PASSWORD`
- `DB_PASSWORD`
- `WEBHOOK_SECRET`
- `SLACK_WEBHOOK_URL` (optional)
- `OPENAI_API_KEY` (for n8n credentials UI)

### 2. Start services

```bash
docker compose up -d
```

Open `http://localhost:5678` and log in with your Basic Auth credentials.

### 3. Import workflows

Import from `workflows/`:

1. `01_support_webhook_intake.json` — **activate in production**
2. `02_demo_csv_batch.json` — manual demo only (keep inactive in prod)
3. `03_error_handler.json` — link as error workflow on 01 and 02

Bind **Postgres Support DB** and **OpenAI Account** credentials on each workflow. Full steps: [docs/runbook.md](docs/runbook.md).

### 4. Test webhook

```bash
pip install -r scripts/requirements.txt
# Load .env, then:
./scripts/test_webhook.sh        # Linux/macOS
# or
./scripts/test_webhook.ps1       # Windows PowerShell
```

### 5. Validate database

```bash
python scripts/validate_tickets.py
```

### 6. Demo CSV batch

In n8n, open **02 Demo CSV Batch**, click **Execute workflow** (manual trigger). Then run `validate_tickets.py` again.

## Webhook contract

```http
POST /webhook/support-intake
X-Webhook-Secret: <WEBHOOK_SECRET>
Content-Type: application/json

{
  "customer_email": "user@example.com",
  "subject": "Subject",
  "body": "Message body",
  "external_id": "optional-id"
}
```

**Responses:** `200` success | `400` invalid payload | `401` invalid secret

## Production deployment

- Enable nginx rate limiting: `docker compose --profile production up -d`
- Set HTTPS URLs in `.env` — see [docs/deployment.md](docs/deployment.md)
- Run Project **02** hardening scan on `workflows/` before import

## Documentation

| Document | Description |
|----------|-------------|
| [docs/runbook.md](docs/runbook.md) | Credentials, activation, checklist |
| [docs/workflow-logic.md](docs/workflow-logic.md) | Business rules and AI behavior |
| [docs/deployment.md](docs/deployment.md) | nginx, TLS, production env |
| [docs/security-baseline.md](docs/security-baseline.md) | Security controls |
| [docs/architecture.md](docs/architecture.md) | System diagram and components |

## Project structure

```
01-n8n-support-automation-pack/
├── docker-compose.yml
├── .env.example
├── demo-data/support_emails.csv
├── nginx/nginx.conf
├── scripts/
│   ├── init-db.sql
│   ├── validate_tickets.py
│   ├── test_webhook.sh
│   └── test_webhook.ps1
├── workflows/
│   ├── 01_support_webhook_intake.json
│   ├── 02_demo_csv_batch.json
│   └── 03_error_handler.json
└── docs/
```

## Design spec

Implementation follows: `docs/superpowers/specs/2026-05-18-n8n-support-automation-design.md` (repository root).

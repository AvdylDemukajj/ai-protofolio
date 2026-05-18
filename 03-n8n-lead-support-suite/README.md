# Project 3: n8n Lead & Support Workflow Suite

**Status:** Production-ready | Secured webhooks | AI lead scoring | Full audit trail

End-to-end **lead lifecycle automation**: ingest leads via webhook or CSV, validate with business rules, score with OpenAI, route hot leads to Slack, and log every decision for compliance.

## Architecture

| Layer | Component |
|-------|-----------|
| Ingestion | Secured webhook + CSV demo batch |
| Validation | Scheduled rules (email, company size, spam hints) |
| Enrichment | OpenAI `gpt-4o-mini` lead scoring |
| Routing | Slack alerts for hot leads (score ≥ 80, confidence ≥ 0.6) |
| Persistence | PostgreSQL `leads` + `lead_audit_log` |
| Runtime | n8n `1.76.1` on port **5679** (avoids conflict with Project 1) |

```
Webhook/CSV → leads (new)
     → Schedule validation → validated | rejected
     → AI scoring → qualified + audit
     → Slack if hot lead
```

## Quick start

### 1. Configure

```bash
cp .env.example .env
# Set N8N_ENCRYPTION_KEY, DB_PASSWORD, WEBHOOK_SECRET, SLACK_WEBHOOK_URL, auth credentials
```

### 2. Start stack

```bash
docker compose up -d
```

- n8n UI: http://localhost:5679  
- Postgres (validation): `localhost:5433` / `leads_db`

### 3. Import workflows

Import from `workflows/` and bind **Postgres Lead DB** + **OpenAI Account**:

| Workflow | Production |
|----------|------------|
| `01_lead_webhook_intake.json` | **Active** |
| `02_lead_validation_schedule.json` | **Active** |
| `03_ai_lead_scoring_routing.json` | **Active** |
| `04_demo_csv_batch.json` | Inactive (demo only) |
| `05_error_handler.json` | Link as error workflow on 01–04 |

Details: [docs/runbook.md](docs/runbook.md)

### 4. Pre-import security scan

```bash
cd ../02-n8n-template-hardening-catalog
pip install -r requirements.txt
python -m scanner ../03-n8n-lead-support-suite/workflows --fail-on HIGH
```

### 5. Test

```bash
pip install -r scripts/requirements.txt
./scripts/test_webhook.sh          # or test_webhook.ps1
# Run workflows 02 and 03 manually or wait for schedule
python scripts/validate_leads.py
```

## Webhook contract

```http
POST /webhook/lead-intake
X-Webhook-Secret: <WEBHOOK_SECRET>

{
  "name": "Jane Doe",
  "email": "jane@company.com",
  "company": "Acme Inc",
  "company_size": 50,
  "message": "Interested in enterprise plan",
  "source": "website",
  "external_id": "crm-123"
}
```

## Business rules (summary)

- **Validation:** valid email, `company_size >= 10`, basic spam filter → `validated` or `rejected`
- **Scoring:** AI returns score 0–100, intent, confidence
- **Slack:** only if `lead_score >= 80`, `confidence >= 0.6`, intent ≠ `spam`
- **Human review:** `requires_human_review = true` when `confidence < 0.6`

Full rules: [docs/workflow-logic.md](docs/workflow-logic.md)

## Documentation

| Doc | Description |
|-----|-------------|
| [docs/runbook.md](docs/runbook.md) | Operations checklist |
| [docs/workflow-logic.md](docs/workflow-logic.md) | Business rules |
| [docs/data-model.md](docs/data-model.md) | Schema reference |
| [docs/architecture.md](docs/architecture.md) | System design |
| [docs/deployment.md](docs/deployment.md) | nginx, TLS, ports |
| [docs/security-baseline.md](docs/security-baseline.md) | Security controls |

## Project structure

```
03-n8n-lead-support-suite/
├── docker-compose.yml
├── database/init.sql, seed_data.sql
├── demo-data/leads_batch_import.csv
├── nginx/nginx.conf
├── workflows/          # 01–05 production workflows
└── scripts/
```

## Ports (portfolio)

| Project | n8n | Postgres |
|---------|-----|----------|
| 01 Support | 5678 | 5434 |
| 03 Leads | **5679** | **5433** |

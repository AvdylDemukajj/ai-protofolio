# Deployment Guide

## Local ports

| Service | URL / Port |
|---------|------------|
| n8n UI | http://localhost:5679 |
| Webhook | http://localhost:5679/webhook/lead-intake |
| Postgres | localhost:5433 (`leads_db`) |
| nginx (production profile) | http://localhost:8081 |

## Environment variables

```env
N8N_PROTOCOL=https
WEBHOOK_URL=https://leads.yourdomain.com/
N8N_EDITOR_BASE_URL=https://leads.yourdomain.com
N8N_ENCRYPTION_KEY=<32+ chars>
DB_PASSWORD=<strong>
WEBHOOK_SECRET=<long random>
SLACK_WEBHOOK_URL=<slack incoming webhook>
```

## Production profile

```bash
docker compose --profile production up -d
```

nginx proxies to n8n and rate-limits `/webhook/` paths (10 req/s, burst 10).

## Running alongside Project 1

Both stacks can run concurrently:

- Project 1: n8n **5678**, Postgres **5434**
- Project 3: n8n **5679**, Postgres **5433**

## Backups

- Volume `postgres_data` — daily snapshots
- Export workflows from n8n after UI changes
- Store secrets in a vault, not git

## CI recommendation

Add to pipeline:

```bash
cd 02-n8n-template-hardening-catalog
python -m scanner ../03-n8n-lead-support-suite/workflows --fail-on HIGH --format sarif -o reports/leads.sarif --quiet
```

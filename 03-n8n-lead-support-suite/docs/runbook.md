# Operations Runbook

## Prerequisites

- Docker Compose
- OpenAI API key (n8n Credentials)
- Slack incoming webhook URL (optional)
- `.env` copied from `.env.example`

## Startup

```bash
docker compose up -d
```

Verify:

- http://localhost:5679 — n8n UI (Basic Auth)
- `pg_isready` on port 5433 — Postgres

## Credential setup

| Credential | Settings |
|------------|----------|
| Postgres Lead DB | Host `db`, Port `5432`, Database `leads_db`, User `leads_user`, Password from `.env` |
| OpenAI Account | API key for `gpt-4o-mini` |

## Workflow activation

| # | File | Active in prod |
|---|------|----------------|
| 01 | `01_lead_webhook_intake.json` | Yes |
| 02 | `02_lead_validation_schedule.json` | Yes |
| 03 | `03_ai_lead_scoring_routing.json` | Yes |
| 04 | `04_demo_csv_batch.json` | No |
| 05 | `05_error_handler.json` | Error workflow link only |

Link **05 Error Handler** on workflows 01–04 via **Settings → Error Workflow**.

## Smoke test sequence

1. `docker compose up -d` — seed data loads 5 sample leads (`status=new`)
2. Activate workflow **01**, run `scripts/test_webhook.sh`
3. Execute **02** manually (or wait 15 min) — validates `new` leads
4. Execute **03** manually — scores `validated` leads
5. `python scripts/validate_leads.py`

## Demo CSV

1. Open **04 Demo CSV Batch**
2. Execute manually
3. Run workflows **02** then **03**

## Production checklist

- [ ] Strong `N8N_ENCRYPTION_KEY`, `DB_PASSWORD`, `WEBHOOK_SECRET`
- [ ] HTTPS `WEBHOOK_URL` and `N8N_EDITOR_BASE_URL`
- [ ] Hardening scan passes `--fail-on HIGH`
- [ ] Workflows 01–03 active; 04 inactive
- [ ] Error handler linked
- [ ] Slack tested with a hot-lead scenario

## Troubleshooting

| Symptom | Action |
|---------|--------|
| 401 on webhook | Check `X-Webhook-Secret` matches `.env` |
| No AI scores | Verify OpenAI credential on workflow 03 |
| Empty Slack | Confirm `SLACK_WEBHOOK_URL` and hot-lead thresholds |
| DB connection failed | Use host `db` inside n8n, `localhost:5433` from host scripts |

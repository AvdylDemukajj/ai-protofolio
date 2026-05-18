# Operations Runbook

## Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Slack incoming webhook URL (optional but recommended)
- Copy `.env.example` to `.env` and set all required values

## 1. Start infrastructure

```bash
cp .env.example .env
# Edit .env — use strong passwords and a 32+ character N8N_ENCRYPTION_KEY

docker compose up -d
```

Open n8n at `http://localhost:5678` and sign in with `N8N_BASIC_AUTH_USER` / `N8N_BASIC_AUTH_PASSWORD`.

## 2. Configure credentials in n8n

Create these credentials in **Settings → Credentials**:

| Credential | Type | Values |
|------------|------|--------|
| Postgres Support DB | Postgres | Host `db`, Port `5432`, DB `n8n`, User `n8n_user`, Password from `.env` `DB_PASSWORD` |
| OpenAI Account | OpenAI | API key from your provider |

Do not paste API keys into workflow node parameters.

## 3. Import workflows

1. **Workflows → Import from File**
2. Import in order:
   - `workflows/01_support_webhook_intake.json`
   - `workflows/02_demo_csv_batch.json`
   - `workflows/03_error_handler.json`
3. Open each Postgres node and select **Postgres Support DB**
4. Open each OpenAI node and select **OpenAI Account**

## 4. Link error handler

1. Open workflow **01 Support Webhook Intake**
2. **Settings → Error Workflow** → select **03 Error Handler**
3. Repeat for **02 Demo CSV Batch**

## 5. Production vs demo activation

| Workflow | Production |
|----------|------------|
| 01 Support Webhook Intake | **Active** |
| 02 Demo CSV Batch | **Inactive** |
| 03 Error Handler | Active via error workflow link (no public trigger) |

## 6. Test webhook

```bash
# Linux/macOS
export $(grep -v '^#' .env | xargs)
./scripts/test_webhook.sh

# Windows PowerShell
Get-Content .env | ForEach-Object { if ($_ -match '^([^#][^=]+)=(.*)$') { Set-Item -Path "env:$($matches[1])" -Value $matches[2] } }
./scripts/test_webhook.ps1
```

Copy the production webhook URL from the **Webhook** node after activating workflow 01.

## 7. Validate database

```bash
pip install -r scripts/requirements.txt
python scripts/validate_tickets.py
```

## 8. Pre-import security scan (recommended)

From repository root, run the Project 02 hardening CLI against `01-n8n-support-automation-pack/workflows/` before importing to production.

## 9. Production profile (nginx rate limit)

```bash
docker compose --profile production up -d
```

Access n8n via `http://localhost:8080`. Configure TLS at your reverse proxy (see `docs/deployment.md`).

## Checklist before go-live

- [ ] Unique `N8N_ENCRYPTION_KEY`, `DB_PASSWORD`, `WEBHOOK_SECRET`
- [ ] `WEBHOOK_URL` / `N8N_EDITOR_BASE_URL` use HTTPS and your real domain
- [ ] Workflow 01 active; workflow 02 inactive
- [ ] Error workflow linked on 01 and 02
- [ ] Slack webhook tested with a high-priority payload
- [ ] `validate_tickets.py` passes after smoke test

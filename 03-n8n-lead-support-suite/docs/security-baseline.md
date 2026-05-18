# Security Baseline

## Credentials

- `.env` is gitignored; never commit secrets
- `N8N_ENCRYPTION_KEY` protects credentials stored in n8n
- OpenAI and Postgres use n8n **Credentials** UI
- Slack URL injected via `$env.SLACK_WEBHOOK_URL` (not hardcoded in workflows)

## Network

- Postgres not required on public internet; port 5433 is for local validation scripts only
- Production: TLS termination at nginx or cloud load balancer
- Internal Docker network `leads-network` between n8n and Postgres

## Webhook security

- Mandatory `X-Webhook-Secret` header
- Optional nginx rate limiting on `/webhook/`
- Payload validation before any `INSERT`

## Data privacy

- `lead_audit_log.input_hash` — SHA-256 of email|name|message
- Full PII remains in `leads` for operations; minimize duplication in logs

## Pre-import gate

Run Project 2 scanner before every production workflow import:

```bash
python -m scanner ./workflows --fail-on HIGH
```

## Disallowed patterns

- Hardcoded API keys or Slack URLs in node parameters
- Execute Command nodes
- Public webhooks without downstream auth validation
- External `http://` URLs (except documented dev hosts)

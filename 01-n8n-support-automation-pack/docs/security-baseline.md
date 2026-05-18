# Security Baseline

## 1. Credential management

- All secrets live in `.env` (gitignored).
- `N8N_ENCRYPTION_KEY` encrypts credentials stored inside n8n.
- OpenAI and database passwords are configured via n8n **Credentials**, not workflow parameters.
- Never commit `.env` or real API keys.

## 2. Access control

- Basic Auth enabled on the n8n UI.
- PostgreSQL is reachable only on the internal Docker network (port `5434` is exposed locally for validation scripts only).
- Webhook callers must send `X-Webhook-Secret` matching `WEBHOOK_SECRET`.

## 3. Webhook hardening

- Reject unauthorized requests with HTTP 401.
- Validate required JSON fields before database writes.
- Optional nginx `limit_req` on `/webhook/` when using the `production` compose profile.
- Use HTTPS in production (`N8N_PROTOCOL=https`, public `WEBHOOK_URL`).

## 4. Data protection

- Customer emails are stored in `support_tickets` for operational use.
- `audit_logs.input_hash` stores SHA-256 of `email|subject|body` instead of duplicating raw content in audit rows.
- `audit_logs.output_json` stores the AI decision payload for traceability.

## 5. Infrastructure

- Official images run as non-root by default.
- Pin container image versions in `docker-compose.yml` (no `latest` in production).
- Run Project 02 workflow hardening scan before importing JSON workflows.

## 6. Operational alerts

- High-priority Slack alerts only when confidence ≥ 0.6.
- Workflow errors are logged to `audit_logs` and optionally sent to Slack via workflow 03.

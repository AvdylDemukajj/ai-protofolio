# Deployment Guide

## Local development

Default stack exposes:

| Service | URL / Port |
|---------|------------|
| n8n UI | `http://localhost:5678` |
| Postgres (validation) | `localhost:5434` |
| Webhook (direct) | `http://localhost:5678/webhook/support-intake` |

## Production profile (nginx)

Start with rate limiting in front of n8n:

```bash
docker compose --profile production up -d
```

| Service | URL / Port |
|---------|------------|
| nginx → n8n | `http://localhost:8080` |
| Webhook via proxy | `http://localhost:8080/webhook/support-intake` |

`nginx/nginx.conf` applies `limit_req` (10 req/s, burst 10) on `/webhook/`.

## HTTPS and public URL

Set in `.env`:

```env
N8N_PROTOCOL=https
WEBHOOK_URL=https://automation.yourdomain.com/
N8N_EDITOR_BASE_URL=https://automation.yourdomain.com
```

Place TLS termination on nginx or an upstream load balancer (Caddy, Traefik, AWS ALB). Forward:

- `Host`
- `X-Forwarded-For`
- `X-Forwarded-Proto`

## Environment variables (production)

| Variable | Required | Notes |
|----------|----------|-------|
| `N8N_ENCRYPTION_KEY` | Yes | 32+ random characters |
| `N8N_BASIC_AUTH_USER` | Yes | UI login |
| `N8N_BASIC_AUTH_PASSWORD` | Yes | Strong password |
| `DB_PASSWORD` | Yes | Postgres password |
| `WEBHOOK_SECRET` | Yes | Shared with webhook callers |
| `WEBHOOK_URL` | Yes | Public base URL for webhooks |
| `SLACK_WEBHOOK_URL` | Recommended | High-priority alerts |
| `OPENAI_API_KEY` | Yes | Configure in n8n credentials UI |

## Caller integration

External systems must send:

```http
POST /webhook/support-intake HTTP/1.1
Host: automation.yourdomain.com
Content-Type: application/json
X-Webhook-Secret: <WEBHOOK_SECRET>

{
  "customer_email": "user@example.com",
  "subject": "Subject line",
  "body": "Message body",
  "external_id": "optional-id"
}
```

## Backups

- Back up Docker volume `postgres_data` regularly.
- Export n8n workflows periodically from the UI.
- Store `.env` secrets in a vault (not in git).

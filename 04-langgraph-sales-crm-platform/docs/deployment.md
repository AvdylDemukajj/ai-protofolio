# Deployment Guide

## Docker Compose (default)

```bash
docker compose up -d --build
```

Services:

- `api` — FastAPI on port 8000
- `frontend` — Streamlit on host port 8502
- `db` — Postgres on host port 5435

## Production recommendations

- Set strong `DB_PASSWORD`, `API_KEY`, `N8N_ENCRYPTION_KEY` equivalent secrets in vault
- Use managed Postgres (RDS, Cloud SQL) and set `DATABASE_URL`
- Enable HTTPS via reverse proxy (Traefik, nginx, ALB)
- Restrict CORS to your dashboard domain (`CORS_ORIGINS`)
- Replace email simulation with SES/SendGrid in `notification.py`
- Set `ENVIRONMENT=production` and valid `OPENAI_API_KEY`

## Scaling

- Run multiple API replicas behind a load balancer (stateless)
- Use Celery/Redis queue if agent runs exceed HTTP timeout (increase uvicorn timeout or async job pattern)
- Streamlit: consider separate review UI or migrate to React + API

## Backups

- Snapshot `postgres_data` volume daily
- Export audit logs for compliance retention

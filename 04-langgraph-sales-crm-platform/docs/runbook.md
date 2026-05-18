# Operations Runbook

## Startup

```bash
cp .env.example .env
docker compose up -d --build
```

Wait for healthy DB, then open:

- API: http://localhost:8000/health
- UI: http://localhost:8502

## Environment

| Variable | Required | Notes |
|----------|----------|-------|
| `DB_PASSWORD` | Yes | Postgres password |
| `OPENAI_API_KEY` | Recommended | Omit for mock LLM mode |
| `API_KEY` | Prod yes | Protects `/leads/*` endpoints |
| `SLACK_WEBHOOK_URL` | Optional | Hot-lead alerts |

## Human-in-the-loop flow

1. Submit lead via Streamlit or `POST /leads/`
2. Agent sets `status=pending_review` when draft exists
3. Reviewer opens dashboard → select lead → **Approve** or **Reject**
4. Approved leads move to `approved` (integrate email provider next)

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `database: down` in health | Check `docker compose logs db`, verify `DB_PASSWORD` |
| 401 on API | Set `X-API-Key` header to match `.env` |
| Mock LLM always on | Provide real `OPENAI_API_KEY` (not `sk-dummy`) |
| Frontend cannot connect | Use `API_URL=http://api:8000` inside Docker; host uses `localhost:8000` |

## Logs

```bash
docker compose logs -f api
docker compose logs -f frontend
```

# Project 4: LangGraph Sales Outreach & CRM Automation

**Status:** Production-ready | Human-in-the-loop | Real OpenAI + mock fallback

Autonomous B2B sales agent: research leads, score intent, draft personalized emails, and route high-value opportunities to Slack — with **human approval** before send.

## Architecture

| Layer | Technology |
|-------|------------|
| Agent | **LangGraph** state machine (research → strategy → draft) |
| API | **FastAPI** (`/leads`, approve/reject, health) |
| UI | **Streamlit** dashboard (port **8502**) |
| Database | **PostgreSQL** (`leads`, `interactions`, `agent_audit_log`) |
| LLM | **OpenAI** `gpt-4o-mini` (mock mode without API key) |

```
Lead form / API → LangGraph agent → PostgreSQL → Streamlit review → Approve/Reject
```

## Quick start

### 1. Configure

```bash
cp .env.example .env
# Set DB_PASSWORD, OPENAI_API_KEY (optional for mock), API_KEY (optional)
```

### 2. Start stack

```bash
docker compose up -d --build
```

| Service | URL |
|---------|-----|
| API docs | http://localhost:8000/docs |
| Dashboard | http://localhost:8502 |
| Postgres | localhost:5435 |

### 3. Smoke test

```bash
pip install -r requirements.txt
python scripts/test_agent_flow.py
curl http://localhost:8000/health
python scripts/validate_api.py --create-lead   # requires API_KEY if set
```

### 4. Run tests

```bash
pytest tests/ -v
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness + DB check |
| POST | `/leads/` | Create lead + run agent |
| GET | `/leads/` | List leads (`?status=pending_review`) |
| GET | `/leads/{id}` | Lead detail |
| POST | `/leads/{id}/approve` | Human approve draft |
| POST | `/leads/{id}/reject` | Human reject |

When `API_KEY` is set in `.env`, send header `X-API-Key` on protected routes.

## Agent behavior

1. **Research** — pain points, score 0–100, intent, strategy (OpenAI or mock)
2. **Strategy** — route: draft (score ≥ 70), more research, or reject
3. **Draft** — subject + body with `requires_human_review=true`
4. **Notify** — Slack when lead is `pending_review` and score ≥ 70

See [docs/agent-behavior-policy.md](docs/agent-behavior-policy.md).

## Project structure

```
04-langgraph-sales-crm-platform/
├── backend/
│   ├── main.py
│   ├── graph/          # LangGraph workflow
│   ├── services/
│   └── Dockerfile
├── frontend/           # Streamlit
├── database/
├── tests/
├── scripts/
└── docs/
```

## Documentation

- [docs/architecture.md](docs/architecture.md)
- [docs/runbook.md](docs/runbook.md)
- [docs/deployment.md](docs/deployment.md)
- [docs/security-audit.md](docs/security-audit.md)
- [docs/agent-behavior-policy.md](docs/agent-behavior-policy.md)

## Portfolio ports

| Project | Service | Port |
|---------|---------|------|
| 01 n8n Support | n8n | 5678 |
| 03 n8n Leads | n8n | 5679 |
| **04 LangGraph CRM** | API / UI / DB | **8000 / 8502 / 5435** |

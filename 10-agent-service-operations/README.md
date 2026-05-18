# Project 10: Agent Service Operations Assistant

## Overview

An operational AI agent with **tool calling** against support systems, protected by **guardrails** that block destructive or unauthorized actions. Every decision is written to an audit log.

## Security & guardrails

- **Policy enforcement**: Blocks `WRITE`/`DELETE` actions in non-production environments.
- **Injection protection**: Detects prompt-injection attempts.
- **Audit trail**: Chat and tool outcomes stored in PostgreSQL.

## Ports (Docker)

| Service | Host port | Container port |
|---------|-----------|----------------|
| API (FastAPI) | **8009** | 8000 |
| Dashboard (Streamlit) | **8510** | 8501 |
| PostgreSQL | **5439** | 5432 |

## Quick start

```bash
cp .env.example .env
# Set OPENAI_API_KEY for live agent responses
docker compose up -d --build
```

- API health: http://localhost:8009/health  
- Dashboard: http://localhost:8510  

Sample tickets (`TICK-101` … `TICK-104`) are loaded from `database/seed_ops_data.sql` on first DB init.

## Local development

```bash
pip install -r requirements.txt
export DATABASE_URL=postgresql://ops_user:SecurePass123!@localhost:5439/ops_db
uvicorn backend.main:app --reload --port 8009
```

## Project layout

- `backend/` — FastAPI app, LangGraph agent, tools, guardrails
- `frontend/` — Streamlit command dashboard
- `database/` — schema + seed data

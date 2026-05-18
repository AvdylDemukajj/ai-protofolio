# Project 06: Multi-Agent SaaS Support Router

## Overview

A **multi-agent orchestration** API that routes support queries to specialized agents (Billing, Technical, Refunds) using **LangGraph**. Each response passes policy guardrails and is persisted with an audit trail in PostgreSQL.

## Architecture

- **Router agent**: Keyword-based intent routing (stable without API keys).
- **Specialized agents**: Billing, Technical, Refunds with scoped mock knowledge.
- **Safety layer**: Policy checks before responses are returned.
- **Persistence**: Conversations and audit logs in PostgreSQL (pgvector image).

## Quick start

```bash
cp .env.example .env
# Optional: set OPENAI_API_KEY for future LLM integrations

docker compose up -d --build
```

API: http://localhost:8000  
Health: `GET /health`  
Chat: `POST /chat` with `{"query": "...", "user_id": "user-1"}`

## Local development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://agent_user:SecurePass123!@localhost:5432/agent_db
uvicorn backend.main:app --reload --port 8000
```

## Tests

```bash
pip install pytest pytest-asyncio
pytest tests/test_routing.py -v
```

## Ports

| Service | Port |
|---------|------|
| API     | 8000 |
| Postgres| 5432 (internal) |

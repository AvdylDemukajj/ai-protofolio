# Project 09: Local AI Invoice Intelligence Dashboard

## Overview

Full-stack invoice automation with **local OCR**, **Ollama LLM** extraction, **math validation**, and a **Streamlit** human-in-the-loop review dashboard. Financial data can stay on your network when `USE_LOCAL_LLM=true`.

## Features

- Local LLM via Ollama (optional cloud fallback)
- Confidence + math checks route low-trust invoices to manual review
- Audit trail for approve/reject actions

## Quick start

```bash
cp .env.example .env
docker compose up -d --build
```

Pull a model inside Ollama (first run):

```bash
docker exec -it local-invoice-ollama ollama pull llama3
```

| Service   | URL |
|-----------|-----|
| API       | http://localhost:8008 |
| Dashboard | http://localhost:8504 |
| Postgres  | localhost:5438 |
| Ollama    | http://localhost:11434 |

## API

- `GET /health`
- `POST /upload`
- `GET /invoices`
- `POST /invoices/{id}/review?action=approve|reject&reviewer=...`

## Status logic

- `needs_review` if subtotal + tax ≠ total (±0.05) or confidence &lt; 0.8
- `extracted` when math and confidence pass

## Local development

```bash
mkdir -p uploads
pip install -r requirements.txt
export DATABASE_URL=postgresql://invoice_user:SecurePass123!@localhost:5438/invoice_db
export UPLOAD_DIR=./uploads
uvicorn backend.main:app --reload --port 8008
```

# Project 07: Invoice Parser & Approval Workflow

## Overview

End-to-end invoice processing: **OCR** and **LLM** extraction, **deterministic math validation**, and a **Streamlit** dashboard for human approval.

## Architecture

- **Backend**: FastAPI, PDF upload, extraction pipeline, PostgreSQL.
- **Frontend**: Streamlit review queue (approve / reject).
- **Validation**: Subtotal + tax must match total; low confidence or high value → manual review.

## Workflow

`uploaded` → `processed` or `needs_review` → `approved` / `rejected`

## Quick start

```bash
cp .env.example .env
# Set OPENAI_API_KEY if using cloud LLM extraction

docker compose up -d --build
```

| Service  | URL |
|----------|-----|
| API      | http://localhost:8006 |
| Dashboard| http://localhost:8503 |
| Postgres | localhost:5437 |

## API

- `GET /health`
- `POST /upload` — multipart PDF
- `GET /invoices`
- `POST /invoices/{id}/review?action=approve|reject`

## Local development

```bash
mkdir -p uploads
pip install -r requirements.txt
export DATABASE_URL=postgresql://invoice_user:SecurePass123!@localhost:5437/invoice_db
export UPLOAD_DIR=./uploads
uvicorn backend.main:app --reload --port 8006
```

Frontend (separate terminal):

```bash
export BACKEND_URL=http://localhost:8006
streamlit run frontend/app.py --server.port 8503
```

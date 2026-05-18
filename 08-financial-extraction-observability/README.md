# Project 08: Financial Data Extraction & Observability Pipeline

## Overview

ETL-style pipeline for financial documents: **Redis** job queue, **MinIO** object storage, background **worker** for OCR/extraction, and **Prometheus/Grafana** observability. Failed jobs retry up to 3 times, then land in a **dead-letter** state.

## Architecture

- **API**: Upload documents, enqueue processing, expose Prometheus metrics.
- **Worker**: Consumes Redis queue, updates document status in PostgreSQL.
- **Retry**: Configurable max retries with DLQ-style terminal state.
- **Observability**: `GET /metrics` (Prometheus format), Grafana on port 3000.

## Quick start

```bash
cp .env.example .env
docker compose up -d --build
```

| Service    | URL |
|------------|-----|
| API        | http://localhost:8007 |
| Metrics    | http://localhost:8007/metrics |
| Prometheus | http://localhost:9090 |
| Grafana    | http://localhost:3000 (admin / admin) |
| MinIO      | http://localhost:9001 |

## API

- `GET /health`
- `GET /metrics` — Prometheus scrape endpoint
- `POST /upload` — multipart file
- `GET /documents/{doc_id}` — processing status

## Local development

```bash
pip install -r requirements.txt
export DB_URL=postgresql://fin_user:SecurePass123!@localhost:5432/fin_db
export REDIS_HOST=localhost
uvicorn backend.main:app --reload --port 8007
```

Worker (separate process):

```bash
python -m backend.worker
```

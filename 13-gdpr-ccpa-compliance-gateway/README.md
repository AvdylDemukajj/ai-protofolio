# Project 13: GDPR/CCPA Compliance Gateway

## Overview

Central privacy gateway implementing **Right to be Forgotten** via the **Saga pattern**: coordinated deletion across PostgreSQL, S3, and analytics with compensating transactions on failure.

## Architecture

- **SagaOrchestrator** — synchronous step execution (no `await` on blocking I/O)
- **Connectors** — PostgreSQL anonymization, S3 object deletion, analytics API
- **AuditLogger** — UUID primary keys for compliance records
- **Postgres schema** — `users`, `sessions`, and `deletion_audit_logs` in `database/init.sql`

## Ports (Docker)

| Service | Host port |
|---------|-----------|
| API | 8013 |
| PostgreSQL | 5436 |

## Quick start

```bash
cp .env.example .env
docker compose up -d --build
curl http://localhost:8013/health
```

### Delete user (demo)

```bash
curl -X POST http://localhost:8013/privacy/delete-user \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-42", "reason": "user_request"}'
```

## Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## API

- `GET /health`
- `POST /privacy/delete-user` — body: `{ "user_id": "...", "reason": "user_request" }`

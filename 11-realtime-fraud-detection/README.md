# Project 11: Real-Time Fraud Detection Engine

## Overview

Event-driven fraud detection using **Apache Kafka**, **Redis** for velocity state, **PostgreSQL** for persistence, and an **Isolation Forest** model for anomaly scoring.

## Architecture

1. **Ingestion**: `data_generator` publishes to Kafka topic `transactions-topic`.
2. **Stream processor**: Rules engine (velocity, amount) + ML risk score.
3. **Persistence**: Transaction row is **inserted before** alerts; status updated after decision.
4. **API**: Manual review endpoints via FastAPI (`api_gateway`).

## Ports (Docker)

| Service | Host port | Notes |
|---------|-----------|-------|
| Kafka | 9092 | External clients |
| Redis | 6379 | Velocity counters |
| PostgreSQL | 5433 | Fraud DB |
| API | 8011 | Review API |

## Quick start

```bash
docker compose up -d --build
docker compose logs -f processor
```

## Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## Key files

- `stream_processor/main.py` — consumer loop
- `stream_processor/alert_service.py` — insert transaction → alert → status update
- `Dockerfile.generator` — Kafka traffic simulator

# Project 14: Multi-Tenant SaaS Platform

## Overview

Production-style **multi-tenant SaaS** API with **schema-per-tenant** isolation in PostgreSQL, Redis-backed tenant resolution, and usage-based billing.

## Architecture

- **Schema-per-tenant**: Each customer gets a dedicated PostgreSQL schema (`tenant_<8-char-id>`).
- **Dynamic routing**: `core/tenant_resolver.py` reads `Host` (or `X-Tenant-Subdomain`) and sets `search_path` safely via `psycopg2.sql.Identifier`.
- **FastAPI**: `api_service/main.py` served by Uvicorn (see `Dockerfile`).
- **Billing**: Hybrid subscription + metered overage — see [docs/billing-logic.md](docs/billing-logic.md).

## Ports (Docker)

| Service | Host port | Container port |
|---------|-----------|----------------|
| API | **8014** | 8000 |
| PostgreSQL | **5434** | 5432 |
| Redis | **6380** | 6379 |

## Quick start

```bash
cp .env.example .env
docker compose up -d --build
curl http://localhost:8014/health
```

### Onboard a tenant

```bash
docker compose exec api python -m onboarding.provision_tenant
```

### API examples

```bash
# List data (tenant from Host header)
curl -H "Host: acme.localhost" http://localhost:8014/api/v1/data

# Or explicit subdomain header when using localhost
curl -H "X-Tenant-Subdomain: acme" http://localhost:8014/api/v1/data
```

## Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

Unit tests use mocks; integration tests (`test_data_isolation_live`) require Postgres on port 5434.

## Project layout

- `api_service/` — FastAPI application
- `core/` — tenant resolver, security helpers
- `billing_engine/` — usage tracking and invoicing
- `onboarding/` — tenant provisioning
- `infrastructure/init_tenant.sql` — master DB + `create_tenant_schema()` function

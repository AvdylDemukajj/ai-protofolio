# Tenant Architecture

## Schema-per-tenant

Each customer receives a dedicated PostgreSQL schema named `tenant_<8-char-hex>` (derived from the tenant UUID). The master `tenants` table stores subdomain, plan, and schema mapping.

## Request routing

1. API receives request with `Host: {subdomain}.example.com` or header `X-Tenant-Subdomain`.
2. `get_tenant_config()` loads metadata from Redis cache or master DB.
3. Connection sets `search_path` using `psycopg2.sql.Identifier` (safe quoting).
4. Queries run only against that tenant's tables (`users`, `data`).

## Isolation guarantee

A bug in application SQL cannot read another tenant's rows while `search_path` is set correctly per request. Cross-tenant access requires an explicit connection to the master catalog.

## Onboarding

`onboarding/provision_tenant.py` inserts a master row and calls `create_tenant_schema()` in PostgreSQL to create schema + standard tables atomically.

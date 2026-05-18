from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Generator, Optional

import json
import os

import psycopg2
import redis
from fastapi import HTTPException, Request
from psycopg2 import sql

redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), decode_responses=True)
MASTER_DB_URL = os.getenv(
    "MASTER_DB_URL",
    "postgresql://saas_admin:SecureRootPass123!@localhost:5432/master_db",
)


def get_tenant_config(subdomain: str) -> Optional[dict]:
    """Fetches tenant config from cache or master DB."""
    cache_key = f"tenant:{subdomain}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    conn = psycopg2.connect(MASTER_DB_URL)
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, schema_name, plan_type, is_active FROM tenants WHERE subdomain = %s",
            (subdomain,),
        )
        row = cur.fetchone()
    finally:
        cur.close()
        conn.close()

    if not row:
        return None

    config = {
        "id": str(row[0]),
        "schema": row[1],
        "plan": row[2],
        "active": row[3],
        "subdomain": subdomain,
    }
    redis_client.setex(cache_key, 300, json.dumps(config))
    return config


def extract_subdomain(request: Request) -> str:
    host = request.headers.get("host", "")
    subdomain = host.split(":")[0].split(".")[0] if host else "default"
    if subdomain in ("www", "api", "localhost", "127", "0"):
        subdomain = request.headers.get("X-Tenant-Subdomain", "default")
    return subdomain


@dataclass
class TenantContext:
    tenant: dict
    conn: Any
    cursor: Any

    def commit(self) -> None:
        self.conn.commit()


@contextmanager
def tenant_connection(schema_name: str) -> Generator[tuple[Any, Any], None, None]:
    conn = psycopg2.connect(MASTER_DB_URL)
    cur = conn.cursor()
    cur.execute(
        sql.SQL("SET search_path TO {}, public").format(sql.Identifier(schema_name))
    )
    try:
        yield conn, cur
    finally:
        cur.close()
        conn.close()


def get_tenant_context(request: Request) -> Generator[TenantContext, None, None]:
    subdomain = extract_subdomain(request)
    tenant = get_tenant_config(subdomain)

    if not tenant or not tenant.get("active"):
        raise HTTPException(status_code=403, detail="Tenant not found or inactive")

    with tenant_connection(tenant["schema"]) as (conn, cur):
        yield TenantContext(tenant=tenant, conn=conn, cursor=cur)


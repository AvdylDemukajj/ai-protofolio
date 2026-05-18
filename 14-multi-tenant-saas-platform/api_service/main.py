import json
from typing import Any, List

from fastapi import Depends, FastAPI
from pydantic import BaseModel

from billing_engine.usage_tracker import track_api_call
from core.tenant_resolver import TenantContext, get_tenant_context

app = FastAPI(title="Multi-Tenant SaaS API", version="1.0.0")


class DataPayload(BaseModel):
    content: Any = {}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/data")
def list_data(ctx: TenantContext = Depends(get_tenant_context)) -> List[dict]:
    ctx.cursor.execute("SELECT id, content FROM data")
    rows = ctx.cursor.fetchall()
    return [{"id": str(row[0]), "content": row[1]} for row in rows]


@app.post("/api/v1/data", status_code=201)
def create_data(
    payload: DataPayload,
    ctx: TenantContext = Depends(get_tenant_context),
) -> dict:
    ctx.cursor.execute(
        "INSERT INTO data (content) VALUES (%s) RETURNING id",
        (json.dumps(payload.content),),
    )
    new_id = ctx.cursor.fetchone()[0]
    ctx.commit()
    track_api_call(ctx.tenant["id"])
    return {
        "id": str(new_id),
        "tenant": ctx.tenant.get("subdomain", "unknown"),
        "status": "created",
    }


@app.get("/api/v1/users")
def get_users(ctx: TenantContext = Depends(get_tenant_context)) -> List[str]:
    ctx.cursor.execute("SELECT email FROM users")
    rows = ctx.cursor.fetchall()
    return [row[0] for row in rows]

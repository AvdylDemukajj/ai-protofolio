import os
from datetime import datetime

import psycopg2

MASTER_DB_URL = os.getenv(
    "MASTER_DB_URL",
    "postgresql://saas_admin:SecureRootPass123!@localhost:5432/master_db",
)

PRICING = {
    "api_call": 0.001,
    "storage_mb": 0.05,
}

PLAN_INCLUDED_API_CALLS = {
    "free": 0,
    "pro": 10_000,
    "enterprise": 100_000,
}

PLAN_BASE_COST = {
    "free": 0.0,
    "pro": 29.0,
    "enterprise": 99.0,
}

OVERAGE_API_RATE = {
    "free": 0.001,
    "pro": 0.0005,
    "enterprise": 0.0003,
}


def generate_monthly_invoice(tenant_id: str, year: int, month: int) -> dict:
    conn = psycopg2.connect(MASTER_DB_URL)
    cur = conn.cursor()

    cur.execute("SELECT plan_type FROM tenants WHERE id = %s", (tenant_id,))
    row = cur.fetchone()
    plan = row[0] if row else "free"

    start_date = datetime(year, month, 1)
    if month < 12:
        end_date = datetime(year, month + 1, 1)
    else:
        end_date = datetime(year + 1, 1, 1)

    cur.execute(
        """
        SELECT event_type, SUM(quantity)
        FROM global_usage_logs
        WHERE tenant_id = %s AND timestamp >= %s AND timestamp < %s
        GROUP BY event_type
        """,
        (tenant_id, start_date, end_date),
    )
    usage_rows = cur.fetchall()

    total_amount = 0.0
    breakdown = []

    base_cost = PLAN_BASE_COST.get(plan, 0.0)
    total_amount += base_cost
    breakdown.append({"item": f"{plan.upper()} Plan Subscription", "cost": base_cost})

    usage_map = {event_type: int(qty) for event_type, qty in usage_rows}

    api_calls = usage_map.get("api_call", 0)
    included = PLAN_INCLUDED_API_CALLS.get(plan, 0)
    billable_calls = max(0, api_calls - included)
    if billable_calls > 0:
        rate = OVERAGE_API_RATE.get(plan, PRICING["api_call"])
        api_cost = billable_calls * rate
        total_amount += api_cost
        breakdown.append(
            {
                "item": f"api_call overage ({billable_calls} of {api_calls} units)",
                "cost": api_cost,
            }
        )

    storage_mb = usage_map.get("storage_mb", 0)
    if storage_mb > 0:
        storage_cost = storage_mb * PRICING["storage_mb"]
        total_amount += storage_cost
        breakdown.append({"item": f"storage_mb ({storage_mb} units)", "cost": storage_cost})

    cur.close()
    conn.close()

    return {"total": round(total_amount, 2), "breakdown": breakdown}

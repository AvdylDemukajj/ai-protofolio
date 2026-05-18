import psycopg2
import os
from datetime import datetime

MASTER_DB_URL = os.getenv('MASTER_DB_URL')

def log_usage(tenant_id: str, event_type: str, quantity: int = 1):
    """Logs usage event to the global billing table."""
    conn = psycopg2.connect(MASTER_DB_URL)
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO global_usage_logs (tenant_id, event_type, quantity, timestamp)
            VALUES (%s, %s, %s, %s)
        """, (tenant_id, event_type, quantity, datetime.now()))
        conn.commit()
    except Exception as e:
        print(f"Billing log failed: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def track_api_call(tenant_id: str):
    log_usage(tenant_id, 'api_call', 1)

def track_storage(tenant_id: str, size_mb: float):
    log_usage(tenant_id, 'storage_mb', int(size_mb))
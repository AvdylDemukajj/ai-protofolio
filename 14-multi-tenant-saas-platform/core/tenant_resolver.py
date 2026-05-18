from functools import wraps
from flask import request, g # Using Flask style context for simplicity, adaptable to FastAPI
import psycopg2
import redis
import json
import os
from psycopg2 import sql

redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), decode_responses=True)
MASTER_DB_URL = os.getenv('MASTER_DB_URL')

def get_tenant_config(subdomain: str):
    """Fetches tenant config from Cache or DB."""
    cache_key = f"tenant:{subdomain}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # Fallback to Master DB
    conn = psycopg2.connect(MASTER_DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT id, schema_name, plan_type, is_active FROM tenants WHERE subdomain = %s", (subdomain,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if not row:
        return None
        
    config = {
        "id": str(row[0]),
        "schema": row[1],
        "plan": row[2],
        "active": row[3]
    }
    
    redis_client.setex(cache_key, 300, json.dumps(config)) # Cache for 5 mins
    return config

def tenant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract subdomain from Host header (e.g., client1.api.com -> client1)
        host = request.headers.get('Host', '')
        subdomain = host.split('.')[0]
        
        if subdomain == 'www' or subdomain == 'api':
            subdomain = 'default' 
            
        tenant = get_tenant_config(subdomain)
        
        if not tenant or not tenant['active']:
            return {"error": "Tenant not found or inactive"}, 403
            
        # Attach tenant info to global context
        g.tenant = tenant
        
        # Create DB connection specific to this tenant's schema
        g.db_conn = psycopg2.connect(MASTER_DB_URL)
        g.db_cursor = g.db_conn.cursor()
        
        # CRITICAL: SET search_path to isolate data
        g.db_cursor.execute(sql.SQL("SET search_path TO %s"), [sql.Identifier(tenant['schema'])])
        
        try:
            return f(*args, **kwargs)
        finally:
            g.db_cursor.close()
            g.db_conn.close()
            
    return decorated_function
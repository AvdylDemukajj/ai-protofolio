import psycopg2
import os
from datetime import datetime

MASTER_DB_URL = os.getenv('MASTER_DB_URL')

PRICING = {
    'api_call': 0.001, # $0.001 per call
    'storage_mb': 0.05 # $0.05 per GB
}

def generate_monthly_invoice(tenant_id: str, year: int, month: int):
    conn = psycopg2.connect(MASTER_DB_URL)
    cur = conn.cursor()
    
    # Get Tenant Plan
    cur.execute("SELECT plan_type FROM tenants WHERE id = %s", (tenant_id,))
    plan = cur.fetchone()[0]
    
    # Calculate Usage
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month+1, 1) if month < 12 else datetime(year+1, 1, 1)
        
    cur.execute("""
        SELECT event_type, SUM(quantity) 
        FROM global_usage_logs 
        WHERE tenant_id = %s AND timestamp BETWEEN %s AND %s
        GROUP BY event_type
    """, (tenant_id, start_date, end_date))
    
    usage_rows = cur.fetchall()
    
    total_amount = 0.0
    breakdown = []
    
    # Base Plan Cost
    base_cost = 0.0
    if plan == 'pro': base_cost = 29.0
    elif plan == 'enterprise': base_cost = 99.0
    
    total_amount += base_cost
    breakdown.append({"item": f"{plan.upper()} Plan Subscription", "cost": base_cost})
    
    # Variable Costs
    for event_type, qty in usage_rows:
        if event_type in PRICING:
            cost = qty * PRICING[event_type]
            total_amount += cost
            breakdown.append({"item": f"{event_type} ({qty} units)", "cost": cost})
            
    cur.close()
    conn.close()
    
    print(f"INVOICE FOR TENANT {tenant_id}: ${total_amount:.2f}")
    return {"total": total_amount, "breakdown": breakdown}
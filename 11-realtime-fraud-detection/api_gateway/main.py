from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
import os
import json

app = FastAPI(title="Fraud Detection API")

def get_db_connection():
    return psycopg2.connect(os.getenv('DB_URL'))

class AlertResponse(BaseModel):
    alert_id: str
    tx_id: str
    amount: float
    user_id: str
    reason: str
    status: str

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(status: str = "open"):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, t.transaction_id, t.amount, t.user_id, a.reason_code, a.status
        FROM fraud_alerts a
        JOIN transactions t ON a.transaction_id = t.id
        WHERE a.status = %s
        ORDER BY a.created_at DESC
        LIMIT 50
    """, (status,))
    
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return [
        AlertResponse(
            alert_id=str(r[0]), tx_id=r[1], amount=float(r[2]), 
            user_id=r[3], reason=r[4], status=r[5]
        ) for r in rows
    ]

@app.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, decision: str, reviewer: str):
    # decision: 'false_positive' or 'confirmed_fraud'
    conn = get_db_connection()
    cur = conn.cursor()
    
    new_status = 'resolved'
    cur.execute("""
        UPDATE fraud_alerts 
        SET status = %s, reviewed_by = %s, reviewed_at = NOW()
        WHERE id = %s
    """, (new_status, reviewer, alert_id))
    
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "success", "message": f"Alert {alert_id} resolved"}
import psycopg2
import json
from typing import Optional

class AlertService:
    def __init__(self, db_url: str):
        self.db_url = db_url

    def create_alert(self, tx_id: str, reason_code: str, details: dict):
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor()
        try:
            # Get internal UUID for transaction
            cur.execute("SELECT id FROM transactions WHERE transaction_id = %s", (tx_id,))
            result = cur.fetchone()
            tx_uuid = result[0] if result else None
            
            if tx_uuid:
                cur.execute("""
                    INSERT INTO fraud_alerts (transaction_id, reason_code, details, status)
                    VALUES (%s, %s, %s, 'open')
                """, (tx_uuid, reason_code, json.dumps(details)))
                conn.commit()
        except Exception as e:
            print(f"Error creating alert: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    def update_transaction_status(self, tx_id: str, status: str, score: float):
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE transactions 
                SET status = %s, risk_score = %s 
                WHERE transaction_id = %s
            """, (status, score, tx_id))
            conn.commit()
        except Exception as e:
            print(f"Error updating tx: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()
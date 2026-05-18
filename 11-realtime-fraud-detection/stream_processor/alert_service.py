import json
from typing import Optional

import psycopg2


class AlertService:
    def __init__(self, db_url: str):
        self.db_url = db_url

    def insert_transaction(
        self,
        tx_id: str,
        user_id: str,
        amount: float,
        currency: str = "USD",
    ) -> Optional[str]:
        """Persists the transaction before alerts or status updates."""
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO transactions (transaction_id, user_id, amount, currency, status)
                VALUES (%s, %s, %s, %s, 'pending')
                ON CONFLICT (transaction_id) DO UPDATE
                SET amount = EXCLUDED.amount, user_id = EXCLUDED.user_id
                RETURNING id
                """,
                (tx_id, user_id, amount, currency),
            )
            row = cur.fetchone()
            conn.commit()
            return str(row[0]) if row else None
        except Exception as exc:
            print(f"Error inserting transaction: {exc}")
            conn.rollback()
            return None
        finally:
            cur.close()
            conn.close()

    def create_alert(self, tx_id: str, reason_code: str, details: dict):
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id FROM transactions WHERE transaction_id = %s",
                (tx_id,),
            )
            result = cur.fetchone()
            tx_uuid = result[0] if result else None

            if tx_uuid:
                cur.execute(
                    """
                    INSERT INTO fraud_alerts (transaction_id, reason_code, details, status)
                    VALUES (%s, %s, %s, 'open')
                    """,
                    (tx_uuid, reason_code, json.dumps(details)),
                )
                conn.commit()
        except Exception as exc:
            print(f"Error creating alert: {exc}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    def update_transaction_status(self, tx_id: str, status: str, score: float):
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor()
        try:
            cur.execute(
                """
                UPDATE transactions
                SET status = %s, risk_score = %s
                WHERE transaction_id = %s
                """,
                (status, score, tx_id),
            )
            conn.commit()
        except Exception as exc:
            print(f"Error updating tx: {exc}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

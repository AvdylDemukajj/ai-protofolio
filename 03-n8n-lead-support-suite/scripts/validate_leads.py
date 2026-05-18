"""Validate lead records and audit logs after running n8n workflows."""

from __future__ import annotations

import os
import sys

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def validate_leads_db() -> None:
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5433")),
            database=os.getenv("DB_NAME", "leads_db"),
            user=os.getenv("DB_USER", "leads_user"),
            password=os.getenv("DB_PASSWORD"),
        )
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM leads")
        total = cur.fetchone()[0]
        print(f"Total leads: {total}")
        assert total > 0, "No leads in database. Run seed, webhook, or CSV workflow first."

        cur.execute(
            "SELECT COUNT(*) FROM leads WHERE status IN ('validated', 'rejected', 'qualified')"
        )
        processed = cur.fetchone()[0]
        print(f"Processed leads (validated/rejected/qualified): {processed}")

        cur.execute("SELECT COUNT(*) FROM leads WHERE lead_score IS NOT NULL")
        scored = cur.fetchone()[0]
        print(f"AI-scored leads: {scored}")

        cur.execute("SELECT COUNT(*) FROM lead_audit_log")
        audits = cur.fetchone()[0]
        print(f"Audit log rows: {audits}")
        assert audits > 0, "No audit rows found. Check workflow audit nodes."

        cur.execute(
            """
            SELECT name, email, company, lead_score, intent_category, status, source
            FROM leads
            ORDER BY created_at DESC
            LIMIT 5
            """
        )
        rows = cur.fetchall()
        print("\nSample leads:")
        for row in rows:
            print(
                f"  - {row[0]} <{row[1]}> | {row[2]} | score={row[3]} "
                f"intent={row[4]} status={row[5]} source={row[6]}"
            )

        cur.close()
        conn.close()
        print("\nAll validation checks passed.")
    except Exception as exc:
        print(f"Validation failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    validate_leads_db()

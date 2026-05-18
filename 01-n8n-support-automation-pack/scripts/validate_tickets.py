"""Validate support tickets and audit logs after running n8n workflows."""

import os
import sys

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def validate_support_db() -> None:
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5434")),
            database=os.getenv("DB_NAME", "n8n"),
            user=os.getenv("DB_USER", "n8n_user"),
            password=os.getenv("DB_PASSWORD"),
        )
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM support_tickets")
        total = cur.fetchone()[0]
        print(f"Total support tickets: {total}")
        assert total > 0, "No tickets found. Run workflow 01 or 02 first."

        cur.execute(
            "SELECT COUNT(*) FROM support_tickets WHERE category IS NOT NULL AND status = 'classified'"
        )
        classified = cur.fetchone()[0]
        print(f"Classified tickets: {classified}")
        assert classified > 0, "No classified tickets. Check OpenAI credentials and workflow execution."

        cur.execute("SELECT COUNT(*) FROM audit_logs WHERE workflow_step = 'classification'")
        audits = cur.fetchone()[0]
        print(f"Classification audit rows: {audits}")
        assert audits > 0, "No classification audit logs found."

        cur.execute(
            "SELECT COUNT(*) FROM support_tickets WHERE priority = 'high'"
        )
        high_priority = cur.fetchone()[0]
        print(f"High-priority tickets: {high_priority}")

        cur.execute(
            """
            SELECT customer_email, subject, category, priority, confidence_score, status, source
            FROM support_tickets
            ORDER BY created_at DESC
            LIMIT 5
            """
        )
        rows = cur.fetchall()
        print("\nSample tickets:")
        for row in rows:
            print(
                f"  - {row[0]} | {row[1][:40]}... | "
                f"cat={row[2]} prio={row[3]} conf={row[4]} status={row[5]} src={row[6]}"
            )

        cur.close()
        conn.close()
        print("\nAll validation checks passed.")
    except Exception as exc:
        print(f"Validation failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    validate_support_db()

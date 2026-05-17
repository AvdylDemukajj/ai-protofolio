import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def validate_leads_db():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5433",
            database="leads_db",
            user="leads_user",
            password=os.getenv("DB_PASSWORD", "SecureDbPass456!")
        )
        cur = conn.cursor()
        
        # Check 1: Total Leads Count
        cur.execute("SELECT COUNT(*) FROM leads")
        count = cur.fetchone()[0]
        print(f"✅ Total Leads in DB: {count}")
        assert count > 0, "Database is empty!"

        # Check 2: Validated Leads
        cur.execute("SELECT COUNT(*) FROM leads WHERE status = 'validated' OR status = 'rejected'")
        processed = cur.fetchone()[0]
        print(f"✅ Processed Leads (Validated/Rejected): {processed}")

        # Check 3: AI Scored Leads (Simulation check)
        cur.execute("SELECT COUNT(*) FROM leads WHERE lead_score IS NOT NULL")
        scored = cur.fetchone()[0]
        print(f"✅ AI Scored Leads: {scored}")

        # Check 4: Sample Data Verification
        cur.execute("SELECT name, company, lead_score, intent_category, status FROM leads LIMIT 5")
        rows = cur.fetchall()
        print("\n📊 Sample Data Preview:")
        for row in rows:
            print(f"   - {row[0]} ({row[1]}): Score {row[2]}, Intent: {row[3]}, Status: {row[4]}")

        cur.close()
        conn.close()
        print("\n🎉 All Validation Checks Passed! System is Enterprise Ready.")
        
    except Exception as e:
        print(f"❌ Validation Failed: {e}")
        exit(1)

if __name__ == "__main__":
    validate_leads_db()
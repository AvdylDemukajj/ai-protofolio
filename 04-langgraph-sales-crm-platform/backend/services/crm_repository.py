from sqlalchemy.orm import Session
from backend.models import LeadStatus
# Import actual SQLAlchemy models if defined (omitted for brevity, using raw SQL for demo)
import psycopg2
from backend.config import settings

def save_lead_result(lead_id: str, analysis: dict, draft: str, decision: str):
    """Saves the AI agent's output to the database."""
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        cur = conn.cursor()
        
        # Update lead with AI data
        cur.execute("""
            UPDATE leads 
            set ai_score = %s, intent_category = %s, draft_email = %s, status = %s
            WHERE id = %s
        """, (
            analysis.get('score'),
            analysis.get('intent'),
            draft,
            'qualified' if 'send' in decision else 'rejected',
            lead_id
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Saved results for lead {lead_id}")
    except Exception as e:
        print(f"❌ Error saving lead: {e}")
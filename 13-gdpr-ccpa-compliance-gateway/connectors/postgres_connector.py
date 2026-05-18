import os
from sqlalchemy import create_engine, text
from core.anonymizer import generate_pseudonym, anonymize_email

class PostgresConnector:
    def __init__(self):
        self.engine = create_engine(os.getenv("DATABASE_URL"))

    def anonymize_user(self, user_id: str):
        """Anonymizes user data instead of hard delete to maintain referential integrity."""
        pseudo_id = generate_pseudonym(user_id)
        
        with self.engine.connect() as conn:
            # Example: Update users table
            conn.execute(text("""
                UPDATE users 
                SET email = :email, 
                    name = 'Deleted User', 
                    external_id = :pseudo_id,
                    deleted_at = NOW()
                WHERE external_id = :user_id
            """), {"email": anonymize_email(f"{user_id}@tmp.com"), "pseudo_id": pseudo_id, "user_id": user_id})
            
            # Example: Delete sensitive sessions
            conn.execute(text("DELETE FROM sessions WHERE user_id = :user_id"), {"user_id": user_id})
            
            conn.commit()
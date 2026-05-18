from sqlalchemy import create_engine, Column, String, Text, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import os

Base = declarative_base()
engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine)

class DeletionAuditLog(Base):
    __tablename__ = "deletion_audit_logs"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    status = Column(String) # success, failed, rolled_back
    steps_completed = Column(Text) # JSON list
    error_message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

class AuditLogger:
    async def log_success(self, user_id: str, steps: list):
        db = SessionLocal()
        log = DeletionAuditLog(user_id=user_id, status="success", steps_completed=str(steps))
        db.add(log)
        db.commit()
        db.close()

    async def log_failure(self, user_id: str, error: str, steps: list):
        db = SessionLocal()
        log = DeletionAuditLog(user_id=user_id, status="failed_rolled_back", error_message=error, steps_completed=str(steps))
        db.add(log)
        db.commit()
        db.close()
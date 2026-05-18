import os
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///./gdpr_audit.db"))
SessionLocal = sessionmaker(bind=engine)


class DeletionAuditLog(Base):
    __tablename__ = "deletion_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False)
    status = Column(String)
    steps_completed = Column(Text)
    error_message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)


class AuditLogger:
    def log_success(self, user_id: str, steps: list) -> None:
        db = SessionLocal()
        try:
            log = DeletionAuditLog(
                user_id=user_id,
                status="success",
                steps_completed=str(steps),
            )
            db.add(log)
            db.commit()
        finally:
            db.close()

    def log_failure(self, user_id: str, error: str, steps: list) -> None:
        db = SessionLocal()
        try:
            log = DeletionAuditLog(
                user_id=user_id,
                status="failed_rolled_back",
                error_message=error,
                steps_completed=str(steps),
            )
            db.add(log)
            db.commit()
        finally:
            db.close()

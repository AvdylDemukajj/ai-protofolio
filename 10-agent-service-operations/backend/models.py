from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from backend.database import Base
from datetime import datetime
import uuid

class SupportTicket(Base):
    __tablename__ = "support_tickets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id_str = Column(String, unique=True, index=True) # e.g., "TICK-101"
    subject = Column(String)
    status = Column(String, default="Open") # Open, In Progress, Resolved, Closed
    priority = Column(String, default="Medium")
    assigned_to = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action_type = Column(String, nullable=False) # e.g., "UPDATE_STATUS", "CREATE_TASK"
    target_resource = Column(String) # e.g., "TICK-101"
    parameters = Column(Text) # JSON string
    agent_decision = Column(Text)
    guardrail_triggered = Column(Boolean, default=False)
    executed_by = Column(String, default="AI_AGENT")
    created_at = Column(DateTime, default=datetime.utcnow)
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from backend.database import Base
from datetime import datetime
import uuid

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, index=True)
    initial_query = Column(Text, nullable=False)
    routed_agent = Column(String)
    final_response = Column(Text)
    risk_level = Column(String) # low, medium, high
    requires_human_review = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    agent_name = Column(String, nullable=False)
    action_type = Column(String)
    input_summary = Column(Text)
    output_summary = Column(Text)
    confidence_score = Column(Integer)
    policy_checks_passed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
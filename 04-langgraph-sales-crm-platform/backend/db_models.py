"""SQLAlchemy ORM models."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class LeadORM(Base):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(255), nullable=False)
    website_url = Column(String(255))
    contact_email = Column(String(255))
    industry = Column(String(100))
    employee_count = Column(Integer)
    pain_points = Column(ARRAY(Text))
    lead_score = Column(Integer)
    buying_intent = Column(String(50))
    outreach_strategy = Column(Text)
    status = Column(String(50), default="new")
    draft_subject = Column(Text)
    draft_body = Column(Text)
    requires_human_review = Column(Boolean, default=True)
    agent_decision = Column(String(100))
    confidence_score = Column(Numeric(3, 2))
    last_interaction_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    interactions = relationship("InteractionORM", back_populates="lead", cascade="all, delete-orphan")
    audit_logs = relationship("AgentAuditLogORM", back_populates="lead", cascade="all, delete-orphan")


class InteractionORM(Base):
    __tablename__ = "interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    interaction_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    ai_generated = Column(Boolean, default=True)
    human_approved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    lead = relationship("LeadORM", back_populates="interactions")


class AgentAuditLogORM(Base):
    __tablename__ = "agent_audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"))
    action_taken = Column(String(100), nullable=False)
    reasoning = Column(Text)
    confidence_score = Column(Numeric(3, 2))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    lead = relationship("LeadORM", back_populates="audit_logs")

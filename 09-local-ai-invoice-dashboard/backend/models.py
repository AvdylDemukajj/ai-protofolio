from sqlalchemy import Column, String, Text, Numeric, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from backend.database import Base
from datetime import datetime
import uuid

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    # Extracted Data
    vendor_name = Column(String)
    invoice_number = Column(String)
    invoice_date = Column(DateTime)
    due_date = Column(DateTime)
    currency = Column(String, default="USD")
    subtotal = Column(Numeric(12, 2))
    tax = Column(Numeric(12, 2))
    total = Column(Numeric(12, 2))
    
    # AI Metrics
    extraction_confidence = Column(Numeric(3, 2), default=0.0)
    
    # Workflow Status
    status = Column(String, default="uploaded") # uploaded, extracted, needs_review, approved, rejected
    reviewed_by = Column(String)
    review_date = Column(DateTime)
    rejection_reason = Column(Text)

class ReviewLog(Base):
    __tablename__ = "review_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), nullable=False)
    reviewer_name = Column(String)
    action = Column(String) # approved, rejected, corrected
    previous_status = Column(String)
    new_status = Column(String)
    comments = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
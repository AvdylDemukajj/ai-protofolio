from sqlalchemy import Column, String, Numeric, Text, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from backend.database import Base
from datetime import datetime
import uuid
import enum

class InvoiceStatus(enum.Enum):
    UPLOADED = "uploaded"
    PROCESSED = "processed"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    
    # Extracted Data
    vendor_name = Column(String)
    invoice_number = Column(String)
    invoice_date = Column(DateTime)
    subtotal = Column(Numeric(12, 2))
    tax = Column(Numeric(12, 2))
    total = Column(Numeric(12, 2))
    currency = Column(String, default="USD")
    
    # AI Metrics
    extraction_confidence = Column(Numeric(3, 2), default=0.0)
    
    # Workflow
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.UPLOADED)
    rejection_reason = Column(Text)
    reviewed_by = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReviewLog(Base):
    __tablename__ = "review_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String, nullable=False) # approved, rejected
    comments = Column(Text)
    reviewer = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
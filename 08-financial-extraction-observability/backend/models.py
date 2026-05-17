from sqlalchemy import Column, String, Text, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from backend.database import Base
from datetime import datetime
import uuid
import enum

class DocumentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    s3_path = Column(String, nullable=False)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING)
    extracted_data = Column(Text) # JSON string
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
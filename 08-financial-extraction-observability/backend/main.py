from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from backend.database import get_db
from backend.models import Document, DocumentStatus
from backend.services.storage_service import storage_service
import redis
import json
import uuid
import structlog
from backend.config import settings

logger = structlog.get_logger()
app = FastAPI(title="Financial Extraction Pipeline", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "financial-pipeline"}

@app.get("/metrics")
def prometheus_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/upload", response_model=dict)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    logger.info(f"Received file: {file.filename}")
    
    try:
        # 1. Save to MinIO
        file_path = f"{uuid.uuid4()}_{file.filename}"
        storage_service.upload_file(file.file, file_path)
        
        # 2. Create DB Record
        new_doc = Document(
            filename=file.filename,
            s3_path=file_path,
            status=DocumentStatus.PENDING
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        
        # 3. Push to Redis Queue
        redis_client = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)
        task_data = {
            "doc_id": str(new_doc.id),
            "filename": file_path,
            "retries": 0
        }
        redis_client.lpush("document_processing_queue", json.dumps(task_data))
        
        logger.info(f"Document {new_doc.id} queued for processing")
        
        return {
            "doc_id": str(new_doc.id),
            "status": "queued",
            "message": "File uploaded and queued for processing"
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{doc_id}")
def get_document_status(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": str(doc.id),
        "filename": doc.filename,
        "status": doc.status.value,
        "extracted_data": doc.extracted_data,
        "error_message": doc.error_message,
        "retry_count": doc.retry_count
    }
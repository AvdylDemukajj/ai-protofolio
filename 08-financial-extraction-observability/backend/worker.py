import os
import redis
import json
import psycopg2
from psycopg2.extras import execute_values
from backend.config import settings
from backend.services.storage_service import storage_service
from backend.services.ocr_service import ocr_service
from backend.services.extraction_service import extraction_service
from backend.utils.retry_handler import RetryHandler
from backend.utils import metrics
import structlog
import time

logger = structlog.get_logger()

def get_db_connection():
    return psycopg2.connect(settings.DB_URL)

def main():
    logger.info("Starting Financial Worker...")
    
    redis_client = redis.Redis(host=settings.REDIS_HOST, port=6379, db=0)
    retry_handler = RetryHandler(redis_client)
    
    queue_name = "document_processing_queue"
    
    while True:
        # Update queue metric
        metrics.QUEUE_SIZE.set(redis_client.llen(queue_name))
        
        # Block waiting for job (BRPOP)
        job = redis_client.brpop(queue_name, timeout=5)
        
        if not job:
            continue
            
        _, job_data_str = job
        job_data = json.loads(job_data_str)
        
        doc_id = job_data.get("doc_id")
        filename = job_data.get("filename")
        
        logger.info(f"Processing document: {doc_id}")
        timer = metrics.start_timer()
        
        try:
            # 1. Update Status to PROCESSING
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE documents SET status = 'processing' WHERE id = %s", (doc_id,))
            conn.commit()
            
            # 2. Download from MinIO (Mocked here as we don't have real file in demo)
            # file_content = storage_service.download(filename) 
            file_content = b"mock_invoice_content" # Mock
            
            # 3. OCR
            raw_text = ocr_service.extract_text(file_content)
            
            # 4. Extract Structured Data
            structured_data = extraction_service.parse_document(raw_text)
            
            # 5. Update DB with Result
            cur.execute("""
                UPDATE documents 
                SET status = 'completed', extracted_data = %s 
                WHERE id = %s
            """, (json.dumps(structured_data), doc_id))
            conn.commit()
            cur.close()
            conn.close()
            
            metrics.track_processing("success")
            metrics.stop_timer(timer)
            logger.info(f"Document {doc_id} processed successfully")
            
        except Exception as e:
            logger.error(f"Error processing {doc_id}: {str(e)}")
            metrics.track_processing("failed")
            
            # Handle Retry or DLQ
            job_data["error"] = str(e)
            retry_handler.retry_task(job_data)
            
            # Update DB status to FAILED or DEAD_LETTER based on retries
            conn = get_db_connection()
            cur = conn.cursor()
            new_status = 'dead_letter' if job_data.get("retries", 0) >= settings.MAX_RETRIES else 'failed'
            cur.execute("""
                UPDATE documents 
                SET status = %s, error_message = %s, retry_count = %s
                WHERE id = %s
            """, (new_status, str(e), job_data.get("retries", 0), doc_id))
            conn.commit()
            cur.close()
            conn.close()

if __name__ == "__main__":
    main()
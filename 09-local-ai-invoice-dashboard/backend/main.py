from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db, SessionLocal
from backend.models import Invoice, ReviewLog
from backend.services.ocr_engine import ocr_engine
from backend.services.llm_extractor import llm_extractor
from backend.services.validation_service import validation_service
from backend.utils.pdf_parser import save_uploaded_file
from backend.config import settings
import structlog
from datetime import datetime

logger = structlog.get_logger()
app = FastAPI(title="Local AI Invoice Intelligence", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/upload", response_model=dict)
async def upload_invoice(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        # 1. Save File
        file_path = save_uploaded_file(file.file, file.filename)
        
        # 2. Extract Text (OCR)
        text_content = ocr_engine.extract_text(file_path)
        
        # 3. Extract Structured Data (LLM)
        extracted_data = await llm_extractor.extract(text_content)
        
        # 4. Validate
        is_math_valid = validation_service.validate_math(extracted_data)
        status = validation_service.check_confidence(extracted_data)
        
        # 5. Save to DB
        new_invoice = Invoice(
            file_name=file.filename,
            file_path=file_path,
            vendor_name=extracted_data.get('vendor_name'),
            invoice_number=extracted_data.get('invoice_number'),
            invoice_date=datetime.strptime(extracted_data.get('invoice_date'), "%Y-%m-%d") if extracted_data.get('invoice_date') else None,
            total=extracted_data.get('total'),
            currency=extracted_data.get('currency'),
            extraction_confidence=extracted_data.get('confidence'),
            status=status
        )
        
        db.add(new_invoice)
        db.commit()
        db.refresh(new_invoice)
        
        return {"id": str(new_invoice.id), "status": status, "data": extracted_data}
        
    except Exception as e:
        logger.error("Upload failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/invoices", response_model=List[dict])
def list_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).order_by(Invoice.upload_date.desc()).all()
    return [
        {
            "id": str(inv.id),
            "file_name": inv.file_name,
            "vendor_name": inv.vendor_name,
            "total": float(inv.total) if inv.total else 0,
            "status": inv.status,
            "extraction_confidence": float(inv.extraction_confidence) if inv.extraction_confidence else 0,
            "invoice_date": str(inv.invoice_date) if inv.invoice_date else None
        } for inv in invoices
    ]

@app.post("/invoices/{invoice_id}/review")
def review_invoice(invoice_id: str, action: str, reviewer: str, comments: str = "", db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Update Status
    new_status = "approved" if action == "approve" else "rejected"
    invoice.status = new_status
    invoice.reviewed_by = reviewer
    invoice.review_date = datetime.utcnow()
    if action == "reject":
        invoice.rejection_reason = comments
    
    # Log Action
    log = ReviewLog(
        invoice_id=invoice.id,
        reviewer_name=reviewer,
        action=action,
        previous_status="needs_review",
        new_status=new_status,
        comments=comments
    )
    db.add(log)
    db.commit()
    
    return {"status": "success", "new_status": new_status}
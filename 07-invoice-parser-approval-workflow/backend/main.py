from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Invoice, InvoiceStatus, ReviewLog
from backend.services.ocr_engine import ocr_engine
from backend.services.llm_extractor import llm_extractor
from backend.services.validation_service import validation_service
from backend.utils.pdf_parser import save_uploaded_file
from backend.config import settings
import structlog
import os

logger = structlog.get_logger()
app = FastAPI(title="Invoice Parser & Approval Workflow", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/upload", response_model=dict)
async def upload_invoice(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # 1. Save File
        content = await file.read()
        file_path = save_uploaded_file(content, file.filename)
        
        # 2. Extract Text (OCR)
        text = ocr_engine.extract_text(file_path)
        
        # 3. Extract Structured Data (LLM)
        data = llm_extractor.extract(text)
        
        # 4. Validate
        math_valid = validation_service.validate_math(data)
        status_str = validation_service.determine_status(data, math_valid)
        status_enum = getattr(InvoiceStatus, status_str.upper(), InvoiceStatus.NEEDS_REVIEW)
        
        # 5. Save to DB
        new_invoice = Invoice(
            file_name=file.filename,
            file_path=file_path,
            vendor_name=data.vendor_name,
            invoice_number=data.invoice_number,
            invoice_date=data.invoice_date,
            subtotal=data.subtotal,
            tax=data.tax,
            total=data.total,
            currency=data.currency,
            extraction_confidence=data.confidence,
            status=status_enum
        )
        
        db.add(new_invoice)
        db.commit()
        db.refresh(new_invoice)
        
        logger.info("Invoice processed", id=str(new_invoice.id), status=status_str)
        
        return {
            "id": str(new_invoice.id),
            "status": status_str,
            "data": data.dict(),
            "message": "Invoice uploaded and processed successfully."
        }
        
    except Exception as e:
        logger.error("Processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/invoices")
def list_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).all()
    return [
        {
            "id": str(inv.id),
            "vendor": inv.vendor_name,
            "total": float(inv.total) if inv.total else 0,
            "status": inv.status.value,
            "confidence": float(inv.extraction_confidence) if inv.extraction_confidence else 0,
            "date": inv.invoice_date
        }
        for inv in invoices
    ]

@app.post("/invoices/{invoice_id}/review")
def submit_review(invoice_id: str, action: str, comments: str = "", reviewer: str = "admin", db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    invoice.status = InvoiceStatus.APPROVED if action == "approve" else InvoiceStatus.REJECTED
    invoice.reviewed_by = reviewer
    if action == "reject":
        invoice.rejection_reason = comments
    
    log = ReviewLog(invoice_id=invoice.id, action=action, comments=comments, reviewer=reviewer)
    db.add(log)
    db.commit()
    
    return {"status": "success", "new_status": invoice.status.value}
import re
import json
import structlog

logger = structlog.get_logger()

class ExtractionService:
    def parse_document(self, text: str) -> dict:
        """Parses raw OCR text into structured JSON."""
        logger.info("Parsing document text...")
        
        data = {
            "raw_text": text,
            "invoice_number": None,
            "total_amount": None,
            "date": None,
            "vendor": None
        }
        
        # Simple Regex patterns for demo
        inv_match = re.search(r"INVOICE\s*#?(\d+)", text, re.IGNORECASE)
        if inv_match:
            data["invoice_number"] = inv_match.group(1)
            
        total_match = re.search(r"Total:\s*\$?([\d,.]+)", text, re.IGNORECASE)
        if total_match:
            data["total_amount"] = total_match.group(1)
            
        vendor_match = re.search(r"Vendor:\s*(\w+)", text, re.IGNORECASE)
        if vendor_match:
            data["vendor"] = vendor_match.group(1)
            
        return data

extraction_service = ExtractionService()
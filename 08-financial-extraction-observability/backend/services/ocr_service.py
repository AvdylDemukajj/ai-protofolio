import structlog
from PIL import Image
import io

logger = structlog.get_logger()

class OCRService:
    def extract_text(self, file_content: bytes) -> str:
        """
        In production, this would call Tesseract or AWS Textract.
        Here we simulate extraction for demo stability.
        """
        logger.info("Simulating OCR process...")
        # Simulate processing time
        import time
        time.sleep(1) 
        
        # Mock result based on filename to make tests deterministic
        if "invoice" in str(file_content).lower():
            return "INVOICE #12345\nTotal: $500.00\nDate: 2024-01-01\nVendor: TechCorp"
        
        return "DOCUMENT CONTENT UNREADABLE OR MOCKED"

ocr_service = OCRService()
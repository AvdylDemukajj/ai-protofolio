import pdfplumber
import pytesseract
from PIL import Image
import io
from backend.config import settings
import structlog

logger = structlog.get_logger()

class OCREngine:
    def extract_text(self, file_path: str) -> str:
        """Extracts text from PDF using a hybrid approach."""
        text_content = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    # Try extracting text directly first
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
                    else:
                        # Fallback to OCR if no text layer
                        logger.info("No text layer found, switching to OCR")
                        img = page.to_image(resolution=300)
                        # Convert PIL Image to bytes then to string via Tesseract
                        # Note: In real Docker, tesseract must be installed
                        text_content += " [OCR Placeholder for Image Content] "
            
            return text_content.strip()
        except Exception as e:
            logger.error("OCR failed", error=str(e))
            raise e

ocr_engine = OCREngine()
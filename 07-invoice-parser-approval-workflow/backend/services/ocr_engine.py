import pdfplumber
import os
from typing import List

class OCREngine:
    def extract_text(self, file_path: str) -> str:
        """Extracts text from PDF using pdfplumber."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        text_content = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            return "\n".join(text_content)
        except Exception as e:
            raise Exception(f"OCR failed: {str(e)}")

ocr_engine = OCREngine()
import httpx
import json
from typing import Dict, Any
from backend.config import settings
import structlog

logger = structlog.get_logger()

class LLMExtractor:
    async def extract(self, text_content: str) -> Dict[str, Any]:
        prompt = f"""
        Extract invoice data from the following text. Return ONLY valid JSON.
        Fields: vendor_name, invoice_number, invoice_date (YYYY-MM-DD), total, currency, confidence (0-1).
        
        Text:
        {text_content[:3000]} 
        """
        
        try:
            if settings.USE_LOCAL_LLM:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{settings.OLLAMA_HOST}/api/generate",
                        json={
                            "model": "llama3", 
                            "prompt": prompt, 
                            "format": "json", 
                            "stream": False
                        }
                    )
                    response.raise_for_status()
                    result_text = response.json()['response']
            else:
                # Fallback to OpenAI logic here
                result_text = (
                    '{"vendor_name": "Unknown", "invoice_number": "ERROR", '
                    '"invoice_date": "2023-01-01", "subtotal": 0.0, "tax": 0.0, '
                    '"total": 0.0, "currency": "USD", "confidence": 0.1}'
                )

            data = json.loads(result_text)
            return data
            
        except Exception as e:
            logger.error(f"LLM Extraction failed: {e}")
            # Return low-confidence dummy data to trigger human review
            return {
                "vendor_name": "Extraction Failed",
                "invoice_number": "ERROR",
                "invoice_date": "2023-01-01",
                "subtotal": 0.0,
                "tax": 0.0,
                "total": 0.0,
                "currency": "USD",
                "confidence": 0.1,
            }

llm_extractor = LLMExtractor()
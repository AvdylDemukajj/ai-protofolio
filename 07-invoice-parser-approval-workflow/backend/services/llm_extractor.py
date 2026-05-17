from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from backend.config import settings
from datetime import datetime

class InvoiceData(BaseModel):
    vendor_name: str = Field(description="Name of the company issuing the invoice")
    invoice_number: str = Field(description="Unique invoice identifier")
    invoice_date: str = Field(description="Date of the invoice in YYYY-MM-DD format")
    subtotal: float = Field(description="Subtotal amount before tax")
    tax: float = Field(description="Tax amount")
    total: float = Field(description="Total amount including tax")
    currency: str = Field(default="USD", description="Currency code")
    confidence: float = Field(description="Confidence score 0.0 to 1.0")

class LLMExtractor:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
        self.parser = PydanticOutputParser(pydantic_object=InvoiceData)

    def extract(self, text: str) -> InvoiceData:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert invoice parser. Extract structured data from the text. If a field is missing, set confidence to 0.5."),
            ("human", "Text:\n{text}\n\nFormat output as JSON.")
        ])
        
        chain = prompt | self.llm | self.parser
        
        try:
            result = chain.invoke({"text": text[:4000]}) # Limit context window
            return result
        except Exception as e:
            # Fallback to low confidence dummy data
            return InvoiceData(
                vendor_name="Unknown",
                invoice_number="ERROR",
                invoice_date=datetime.now().strftime("%Y-%m-%d"),
                subtotal=0.0,
                tax=0.0,
                total=0.0,
                confidence=0.1
            )

llm_extractor = LLMExtractor()
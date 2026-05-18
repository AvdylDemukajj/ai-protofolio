from pydantic import BaseModel
from typing import List

class InvoiceItem(BaseModel):
    item: str
    cost: float

class Invoice(BaseModel):
    tenant_id: str
    total: float
    breakdown: List[InvoiceItem]
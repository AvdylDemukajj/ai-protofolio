from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Literal
from datetime import datetime

class LeadCreate(BaseModel):
    company_name: str = Field(..., min_length=2)
    website_url: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None

class LeadAnalysis(BaseModel):
    pain_points: List[str] = []
    lead_score: int = Field(ge=0, le=100)
    buying_intent: Literal['cold', 'warm', 'hot']
    outreach_strategy: str
    confidence: float = Field(ge=0.0, le=1.0)

class OutreachDraft(BaseModel):
    subject: str
    body: str
    tone: str = "professional"
    requires_human_review: bool = True

class AgentDecision(BaseModel):
    action: Literal["research", "draft_email", "schedule_followup", "reject"]
    reasoning: str
    risk_level: Literal["low", "medium", "high"]
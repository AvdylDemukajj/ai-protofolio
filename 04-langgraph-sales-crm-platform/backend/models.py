"""Pydantic API schemas."""

from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LeadCreate(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=255)
    website_url: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None
    industry: Optional[str] = Field(None, max_length=100)
    employee_count: Optional[int] = Field(None, ge=0)


class LeadAnalysis(BaseModel):
    pain_points: List[str] = Field(default_factory=list)
    lead_score: int = Field(ge=0, le=100)
    buying_intent: Literal["cold", "warm", "hot"]
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


class LeadResponse(BaseModel):
    id: UUID
    company_name: str
    website_url: Optional[str] = None
    contact_email: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    pain_points: List[str] = Field(default_factory=list)
    lead_score: Optional[int] = None
    buying_intent: Optional[str] = None
    outreach_strategy: Optional[str] = None
    status: str
    draft_subject: Optional[str] = None
    draft_body: Optional[str] = None
    requires_human_review: bool = True
    agent_decision: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AgentRunResponse(BaseModel):
    status: str
    lead_id: UUID
    lead: LeadResponse
    agent_messages: List[str] = Field(default_factory=list)
    decision: Optional[str] = None

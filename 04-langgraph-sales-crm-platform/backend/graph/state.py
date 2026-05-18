"""LangGraph agent state definition."""

from typing import Optional, TypedDict

from backend.models import AgentDecision, LeadAnalysis, OutreachDraft


class AgentState(TypedDict, total=False):
    lead_id: str
    company_info: dict
    analysis: Optional[LeadAnalysis]
    draft: Optional[OutreachDraft]
    decision: Optional[AgentDecision]
    messages: list[str]
    error: Optional[str]
    research_iterations: int

from typing import TypedDict, Optional, List
from backend.models import LeadAnalysis, OutreachDraft, AgentDecision

class AgentState(TypedDict):
    lead_id: str
    company_info: dict
    analysis: Optional[LeadAnalysis]
    draft: Optional[OutreachDraft]
    decision: Optional[AgentDecision]
    messages: List[str]
    error: Optional[str]
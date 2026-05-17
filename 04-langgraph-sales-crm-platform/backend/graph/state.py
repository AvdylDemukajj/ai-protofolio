from typing import TypedDict, Optional

class AgentState(TypedDict):
    lead_id: str
    analysis: Optional[dict]
    draft: Optional[str]
    decision: Optional[str]
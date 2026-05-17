from typing import TypedDict, Optional, Dict, Any

class AgentState(TypedDict):
    query: str
    routing_decision: Optional[str]
    response: Optional[Dict[str, Any]]
    error: Optional[str]
    requires_human_review: bool
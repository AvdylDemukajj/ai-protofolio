from backend.agents.base_agent import BaseAgent
from typing import List, Dict, Any

class RouterAgent(BaseAgent):
    def __init__(self):
        super().__init__("Router", "system")

    async def retrieve_context(self, query: str) -> List[str]:
        return [] # Router doesn't need RAG

    async def generate_response(self, query: str, docs: List[str]) -> str:
        # Simple keyword-based routing logic for reliability
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["bill", "pay", "invoice", "charge", "refund"]):
            return "billing"
        elif any(word in query_lower for word in ["error", "bug", "login", "api", "tech", "slow"]):
            return "technical"
        elif any(word in query_lower for word in ["cancel", "return", "money back"]):
            return "refunds"
        
        return "general"

router_agent = RouterAgent()
from backend.agents.base_agent import BaseAgent
from typing import List

class RefundAgent(BaseAgent):
    def __init__(self):
        super().__init__("RefundAgent", "refunds")

    async def retrieve_context(self, query: str) -> List[str]:
        return ["Refunds are processed within 5-7 business days.", "Items must be unused."]

    async def generate_response(self, query: str, docs: List[str]) -> str:
        # Guardrail: Never promise specific amounts without approval
        if "$" in query or "amount" in query.lower():
            return "I can initiate a refund request, but the final amount must be approved by a manager."
        return f"Refund Policy: {docs[0]}"

refunds_agent = RefundsAgent()
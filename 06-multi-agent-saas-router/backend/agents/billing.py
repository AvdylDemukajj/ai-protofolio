from backend.agents.base_agent import BaseAgent
from typing import List

class BillingAgent(BaseAgent):
    def __init__(self):
        super().__init__("BillingAgent", "billing")

    async def retrieve_context(self, query: str) -> List[str]:
        # Mock retrieval from Billing Knowledge Base
        return ["Invoices are generated on the 1st of each month.", "Payment methods include Credit Card and Wire Transfer."]

    async def generate_response(self, query: str, docs: List[str]) -> str:
        return f"Based on our billing policy: {docs[0]} Please contact finance@company.com for specific invoice requests."

billing_agent = BillingAgent()
from backend.agents.base_agent import BaseAgent
from typing import List

class TechnicalAgent(BaseAgent):
    def __init__(self):
        super().__init__("TechnicalAgent", "technical")

    async def retrieve_context(self, query: str) -> List[str]:
        return ["For login issues, try resetting your password.", "API Rate limits are 1000 req/min."]

    async def generate_response(self, query: str, docs: List[str]) -> str:
        return f"Technical Support suggests: {docs[0]} If the issue persists, please open a ticket."

technical_agent = TechnicalAgent()
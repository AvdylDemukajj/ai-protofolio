from abc import ABC, abstractmethod
from typing import List, Dict, Any
from backend.services.audit_logger import log_agent_action
from backend.utils.validators import check_policy_violations
import structlog

logger = structlog.get_logger()

class BaseAgent(ABC):
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category

    async def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 1. Retrieve Context (RAG simulation for demo)
            retrieved_docs = await self.retrieve_context(query)
            
            # 2. Generate Response (Mock LLM call for stability in demo)
            response_text = await self.generate_response(query, retrieved_docs)
            
            # 3. Safety Check (Guardrails)
            violations = check_policy_violations(response_text, self.category)
            
            result = {
                "answer": response_text,
                "sources": retrieved_docs,
                "requires_human_review": len(violations) > 0,
                "policy_violations": violations,
                "confidence": 95 if not violations else 40
            }

            # 4. Audit Log
            await log_agent_action(
                agent_name=self.name,
                action_type="process_query",
                input_summary=query[:50],
                output_summary=response_text[:50],
                confidence=result["confidence"],
                policy_checks_passed=len(violations) == 0
            )
            
            return result
        except Exception as e:
            logger.error(f"Agent {self.name} failed", error=str(e))
            raise e

    @abstractmethod
    async def retrieve_context(self, query: str) -> List[str]:
        pass

    @abstractmethod
    async def generate_response(self, query: str, docs: List[str]) -> str:
        pass
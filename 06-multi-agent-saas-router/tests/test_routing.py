"""Basic routing tests for the multi-agent workflow."""

import pytest

from backend.graph.workflow import should_route
from backend.agents.router import router_agent


@pytest.mark.parametrize(
    "decision,expected",
    [
        ("billing", "billing"),
        ("technical", "technical"),
        ("refunds", "refunds"),
        ("general", "human_escalation"),
        (None, "human_escalation"),
    ],
)
def test_should_route(decision, expected):
    assert should_route({"routing_decision": decision}) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query,expected_agent",
    [
        ("I was charged twice on my invoice", "billing"),
        ("The API returns a 500 error", "technical"),
        ("I want my money back and cancel", "refunds"),
        ("Hello, what are your hours?", "general"),
    ],
)
async def test_router_agent_keywords(query, expected_agent):
    result = await router_agent.process(query, {})
    assert result["answer"] == expected_agent

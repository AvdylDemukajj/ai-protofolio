"""Tests for LangGraph agent workflow."""

from backend.graph.workflow import agent_graph


def test_high_value_lead_produces_draft():
    state = {
        "lead_id": "test-0001",
        "company_info": {
            "company_name": "Global Finance Corp",
            "industry": "Finance",
            "employee_count": 500,
        },
        "messages": [],
        "analysis": None,
        "draft": None,
        "decision": None,
        "error": None,
        "research_iterations": 0,
    }
    result = agent_graph.invoke(state)
    assert result["analysis"] is not None
    assert result["analysis"].lead_score >= 70
    assert result["draft"] is not None
    assert result["draft"].subject
    assert result["decision"] is not None


def test_low_value_lead_rejected():
    state = {
        "lead_id": "test-0002",
        "company_info": {
            "company_name": "Tiny Shop",
            "industry": "Retail",
            "employee_count": 3,
        },
        "messages": [],
        "analysis": None,
        "draft": None,
        "decision": None,
        "error": None,
        "research_iterations": 0,
    }
    result = agent_graph.invoke(state)
    assert result["analysis"] is not None
    assert result["analysis"].lead_score < 70
    assert result.get("draft") is None or result["decision"].action == "reject"

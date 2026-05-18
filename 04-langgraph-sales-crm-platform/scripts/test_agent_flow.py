"""Manual smoke test for the LangGraph sales agent."""

from backend.graph.workflow import agent_graph


def main() -> None:
    print("Testing high-value lead scenario...")
    state = {
        "lead_id": "manual-test-001",
        "company_info": {
            "company_name": "Global Corp",
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
    print(f"  Score: {result['analysis'].lead_score}")
    print(f"  Decision: {result['decision'].action if result.get('decision') else 'N/A'}")
    if result.get("draft"):
        print(f"  Subject: {result['draft'].subject}")
    print("All checks passed.")


if __name__ == "__main__":
    main()

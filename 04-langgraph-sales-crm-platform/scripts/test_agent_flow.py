from backend.graph.workflow import app as agent_graph

def test_high_value_lead():
    print("🧪 Testing High Value Lead Scenario...")
    
    state = {
        "lead_id": "test-123",
        "company_info": {
            "company_name": "Global Corp",
            "industry": "Finance",
            "employee_count": 500
        },
        "messages": [],
        "analysis": None,
        "draft": None,
        "decision": None,
        "error": None
    }
    
    result = agent_graph.invoke(state)
    
    assert result["analysis"] is not None, "Analysis failed"
    assert result["analysis"].lead_score > 70, "Scoring logic failed for high value lead"
    assert result["draft"] is not None, "Drafting failed"
    assert result["decision"].action == "draft_email", "Routing logic failed"
    
    print("✅ Test Passed!")
    print(f"   Score: {result['analysis'].lead_score}")
    print(f"   Action: {result['decision'].action}")
    print(f"   Draft Subject: {result['draft'].subject}")

if __name__ == "__main__":
    test_high_value_lead()
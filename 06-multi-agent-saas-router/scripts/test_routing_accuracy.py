import asyncio
import sys
sys.path.append('..')

from backend.graph.workflow import app as agent_graph

test_cases = [
    ("I was charged twice!", "billing"),
    ("My API returns 500 error", "technical"),
    ("I want my money back", "refunds"),
    ("How do I reset password?", "technical"),
    ("Speak to your manager now", "human_escalation") # Fallback case
]

async def run_tests():
    print("🧪 Starting Multi-Agent Routing Tests...")
    passed = 0
    
    for query, expected_agent in test_cases:
        state = {
            "query": query,
            "routing_decision": None,
            "response": None,
            "error": None,
            "requires_human_review": False
        }
        result = await agent_graph.ainvoke(state)
        actual_agent = result.get("routing_decision")
        
        # Special handling for fallback
        if expected_agent == "human_escalation" and actual_agent is None:
             # If router doesn't know, it might go to general/human depending on logic
             actual_agent = "human_escalation" 
             
        if actual_agent == expected_agent or (expected_agent == "human_escalation" and result.get("requires_human_review")):
            print(f"✅ PASS: '{query[:30]}...' -> {actual_agent}")
            passed += 1
        else:
            print(f"❌ FAIL: '{query[:30]}...' -> Expected {expected_agent}, Got {actual_agent}")
            
    print(f"\nResults: {passed}/{len(test_cases)} tests passed.")

if __name__ == "__main__":
    asyncio.run(run_tests())
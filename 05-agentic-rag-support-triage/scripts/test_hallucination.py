import sys
sys.path.append('.')

from backend.services.rag_engine import RAGEngine
from backend.services.validation_service import ValidationService

def test_rag_flow():
    print("🧪 Testing RAG Flow...")
    
    engine = RAGEngine()
    validator = ValidationService()
    
    # Mock context for testing without DB
    mock_context = ["We ship within 24 hours.", "Returns accepted in 14 days."]
    
    query = "How fast do you ship?"
    answer = engine.generate_answer(query, mock_context)
    
    print(f"Query: {query}")
    print(f"Answer: {answer}")
    
    is_grounded = validator.check_grounding(answer, mock_context)
    print(f"Grounded: {is_grounded}")
    
    if is_grounded:
        print("✅ Test Passed: Answer is grounded in context.")
    else:
        print("❌ Test Failed: Answer might be hallucinated.")

if __name__ == "__main__":
    test_rag_flow()
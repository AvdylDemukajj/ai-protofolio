"""Manual check for grounding validation on sample Q&A."""

from backend.rag_engine import rag_engine
from backend.validators import validation_service


def main() -> None:
    question = "How long do I have to return a product?"
    context = rag_engine.retrieve_context(question)
    answer = rag_engine.generate_answer(question, context)
    grounded = validation_service.check_grounding(answer, context)
    safe = validation_service.check_safety(answer)
    print(f"Question: {question}")
    print(f"Answer: {answer[:200]}...")
    print(f"Grounded: {grounded} | Safe: {safe}")


if __name__ == "__main__":
    main()

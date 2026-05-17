def retrieve_context(query: str):
    return ["Policy Document A", "FAQ Item B"]

def generate_answer(query: str, context: list):
    return f"Based on {context[0]}, the answer is..."
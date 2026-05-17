class RouterAgent:
    def route(self, query: str) -> str:
        if "billing" in query.lower(): return "billing"
        return "general"
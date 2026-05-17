from langgraph.graph import StateGraph, END
from backend.graph.state import AgentState
from backend.graph.nodes import research_node, strategy_node, draft_node

def route_logic(state: AgentState) -> str:
    decision = state.get("decision")
    if not decision:
        return "error"
    
    if decision.action == "research":
        return "research"
    elif decision.action == "draft_email":
        return "draft"
    elif decision.action == "reject":
        return "end"
    return "end"

workflow = StateGraph(AgentState)

workflow.add_node("research", research_node)
workflow.add_node("strategy", strategy_node)
workflow.add_node("draft", draft_node)

workflow.set_entry_point("strategy")

workflow.add_conditional_edges(
    source="strategy",
    cond=route_logic,
    mapping={
        "research": "research",
        "draft": "draft",
        "end": END,
        "error": END
    }
)

workflow.add_edge("research", "strategy")
workflow.add_edge("draft", END)

app = workflow.compile()
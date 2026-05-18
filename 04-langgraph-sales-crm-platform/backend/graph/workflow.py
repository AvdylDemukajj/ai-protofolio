"""LangGraph workflow definition: research → strategy → draft/reject."""

from langgraph.graph import END, StateGraph

from backend.graph.nodes import draft_node, research_node, strategy_node
from backend.graph.state import AgentState


def route_after_strategy(state: AgentState) -> str:
    decision = state.get("decision")
    if not decision:
        return "error"
    action = decision.action
    if action == "research":
        if state.get("research_iterations", 0) >= 2:
            return "reject"
        return "research"
    if action == "draft_email":
        return "draft"
    if action == "reject":
        return "reject"
    return "reject"


workflow = StateGraph(AgentState)

workflow.add_node("research", research_node)
workflow.add_node("strategy", strategy_node)
workflow.add_node("draft", draft_node)

workflow.set_entry_point("research")
workflow.add_edge("research", "strategy")
workflow.add_conditional_edges(
    "strategy",
    route_after_strategy,
    {
        "research": "research",
        "draft": "draft",
        "reject": END,
        "error": END,
    },
)
workflow.add_edge("draft", END)

agent_graph = workflow.compile()

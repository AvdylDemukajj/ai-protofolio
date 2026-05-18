from langgraph.graph import StateGraph, END
from backend.graph.state import AgentState
from backend.agents.router import router_agent
from backend.agents.billing import billing_agent
from backend.agents.technical import technical_agent
from backend.agents.refunds import refunds_agent

async def route_node(state: AgentState) -> AgentState:
    decision = await router_agent.process(state["query"], {})
    # The "response" from router is actually the target agent name
    return {"routing_decision": decision["answer"]}

def should_route(state: AgentState) -> str:
    decision = state.get("routing_decision")
    if decision == "billing": return "billing"
    if decision == "technical": return "technical"
    if decision == "refunds": return "refunds"
    return "human_escalation"

async def handle_billing(state: AgentState) -> AgentState:
    resp = await billing_agent.process(state["query"], {})
    return {"response": resp, "requires_human_review": resp["requires_human_review"]}

async def handle_technical(state: AgentState) -> AgentState:
    resp = await technical_agent.process(state["query"], {})
    return {"response": resp, "requires_human_review": resp["requires_human_review"]}

async def handle_refunds(state: AgentState) -> AgentState:
    resp = await refunds_agent.process(state["query"], {})
    return {"response": resp, "requires_human_review": resp["requires_human_review"]}

async def human_escalation(state: AgentState) -> AgentState:
    return {
        "response": {
            "answer": "Your request is complex and has been escalated to a human specialist.",
            "requires_human_review": True,
            "confidence": 0
        },
        "requires_human_review": True
    }

# Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("route", route_node)
workflow.add_node("billing", handle_billing)
workflow.add_node("technical", handle_technical)
workflow.add_node("refunds", handle_refunds)
workflow.add_node("human_escalation", human_escalation)

workflow.set_entry_point("route")

workflow.add_conditional_edges(
    "route",
    should_route,
    {
        "billing": "billing",
        "technical": "technical",
        "refunds": "refunds",
        "human_escalation": "human_escalation",
    },
)

workflow.add_edge("billing", END)
workflow.add_edge("technical", END)
workflow.add_edge("refunds", END)
workflow.add_edge("human_escalation", END)

app = workflow.compile()
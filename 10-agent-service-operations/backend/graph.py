from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from typing import TypedDict, List, Annotated
import operator
from backend.tools import get_ticket_status, update_ticket_status, assign_ticket
from backend.guards import safety_guard
from backend.config import settings
from backend.utils.logger import logger

# Define State
class AgentState(TypedDict):
    messages: Annotated[List, operator.add]
    blocked: bool

# Define Tools
tools = [get_ticket_status, update_ticket_status, assign_ticket]
llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0).bind_tools(tools)

def agent_node(state: AgentState):
    messages = state["messages"]
    
    # Check for injection before sending to LLM
    last_msg = messages[-1].content if messages else ""
    if safety_guard.check_injection_attempt(str(last_msg)):
        return {"messages": [AIMessage(content="⛔ Security Alert: Potential prompt injection detected. Action blocked.")], "blocked": True}

    response = llm.invoke(messages)
    return {"messages": [response], "blocked": False}

def tool_node(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {"messages": [], "blocked": False}

    results = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        args = tool_call["args"]
        
        # SAFETY CHECK BEFORE EXECUTION
        if safety_guard.check_destructive_action(tool_name, args):
            logger.critical("GUARDRAIL TRIGGERED", tool=tool_name, args=args)
            results.append(ToolMessage(
                content=f"⛔ ACTION BLOCKED: The tool '{tool_name}' cannot be executed due to safety policies (Environment: {settings.ENVIRONMENT}).",
                tool_call_id=tool_call["id"]
            ))
        else:
            # Execute Tool
            try:
                if tool_name == "get_ticket_status":
                    res = get_ticket_status(args["ticket_id"])
                elif tool_name == "update_ticket_status":
                    res = update_ticket_status(args["ticket_id"], args["new_status"], args.get("reason", ""))
                elif tool_name == "assign_ticket":
                    res = assign_ticket(args["ticket_id"], args["agent_name"])
                else:
                    res = "Unknown tool."
                
                results.append(ToolMessage(content=res, tool_call_id=tool_call["id"]))
            except Exception as e:
                results.append(ToolMessage(content=f"Error: {str(e)}", tool_call_id=tool_call["id"]))

    return {"messages": results, "blocked": False}

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    
    if isinstance(last_message, ToolMessage):
        return "agent" # Go back to agent to formulate final answer
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    return END

# Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "END": END})
workflow.add_edge("tools", "agent")

app = workflow.compile()
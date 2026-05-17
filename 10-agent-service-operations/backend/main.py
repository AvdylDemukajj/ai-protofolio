from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.graph import app as agent_graph
from langchain_core.messages import HumanMessage
from backend.database import SessionLocal, get_db
from backend.models import AuditLog
import json

app = FastAPI(title="Agent Service Operations Assistant", version="1.0.0")

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = []

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(request: ChatRequest):
    # Construct state
    messages = [HumanMessage(content=m["content"]) if m["role"]=="user" else AIMessage(content=m["content"]) for m in request.conversation_history]
    messages.append(HumanMessage(content=request.message))
    
    initial_state = {"messages": messages, "blocked": False}
    
    try:
        result = await agent_graph.ainvoke(initial_state)
        final_response = result["messages"][-1].content
        
        # Log to Audit DB if tools were used
        # Simplified logging for demo
        db = SessionLocal()
        log = AuditLog(
            action_type="CHAT_INTERACTION",
            target_resource="N/A",
            parameters=json.dumps({"input": request.message}),
            agent_decision=final_response[:500],
            guardrail_triggered=result.get("blocked", False)
        )
        db.add(log)
        db.commit()
        db.close()
        
        return {"response": final_response, "blocked": result.get("blocked", False)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.graph.workflow import app as agent_graph
from backend.database import SessionLocal, get_db
from backend.models import Conversation
import structlog

logger = structlog.get_logger()
app = FastAPI(title="Multi-Agent SaaS Router", version="1.0.0")

class QueryRequest(BaseModel):
    query: str
    user_id: str = "anonymous"

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(request: QueryRequest):
    logger.info("Received chat request", query=request.query)
    
    try:
        initial_state = {
            "query": request.query,
            "routing_decision": None,
            "response": None,
            "error": None,
            "requires_human_review": False
        }
        
        result = await agent_graph.ainvoke(initial_state)
        
        # Save conversation to DB
        db = SessionLocal()
        conv = Conversation(
            user_id=request.user_id,
            initial_query=request.query,
            routed_agent=result.get("routing_decision"),
            final_response=result.get("response", {}).get("answer", ""),
            risk_level="high" if result.get("requires_human_review") else "low",
            requires_human_review=result.get("requires_human_review")
        )
        db.add(conv)
        db.commit()
        db.close()
        
        return result
        
    except Exception as e:
        logger.error("Chat processing failed", error=str(e))
        raise HTTPException(status_code=500, detail="Agent processing failed")
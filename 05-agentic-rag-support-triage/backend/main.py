from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from backend.services.rag_engine import rag_engine
from backend.services.validation_service import validation_service
from backend.utils.logger import logger
from backend.database import get_db, SessionLocal
from backend.models import InteractionLog
import time

app = FastAPI(title="Agentic RAG Support Triage", version="1.0.0")

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    verified: bool
    confidence_score: int

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "rag-support-api"}

@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    start_time = time.time()
    try:
        # Retrieve relevant context from the knowledge base
        context = rag_engine.retrieve_context(request.question)
        
        # Generate answer using retrieved context
        answer = rag_engine.generate_answer(request.question, context)
        
        # Validate grounding and safety
        grounding = validation_service.check_grounding(answer, context)
        safe = validation_service.check_safety(answer)
        verified = grounding and safe
        confidence_score = int(grounding) * 70 + int(safe) * 30  # Example scoring

        # Prepare sources (for now, source titles from context)
        sources = [c[:40] + "..." if len(c) > 40 else c for c in context]

        # Log interaction
        db = SessionLocal()
        log = InteractionLog(
            query=request.question,
            response=answer,
            sources_used=', '.join(sources),
            confidence_score=confidence_score
        )
        db.add(log)
        db.commit()
        db.close()

        logger.info(
            "Answered user query",
            question=request.question,
            answer=answer,
            verified=verified,
            confidence_score=confidence_score,
            duration=time.time() - start_time
        )

        return QueryResponse(
            answer=answer,
            sources=sources,
            verified=verified,
            confidence_score=confidence_score
        )
    except Exception as e:
        logger.error("Failed to answer question", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
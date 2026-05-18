"""FastAPI service for agentic RAG support triage."""

from __future__ import annotations

import time
from typing import List, Optional

import structlog
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import check_db, get_db
from backend.logger import logger
from backend.models import InteractionLog
from backend.rag_engine import rag_engine
from backend.validators import validation_service

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ]
)

app = FastAPI(title="Agentic RAG Support Triage", version="2.0.0")


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    verified: bool
    confidence_score: int


def verify_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    if settings.API_KEY and x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.on_event("startup")
def startup_index():
    from backend.database import SessionLocal
    from backend.models import KnowledgeDocument

    db = SessionLocal()
    try:
        count = db.query(KnowledgeDocument).count()
        if count == 0:
            indexed = rag_engine.index_markdown_folder()
            logger.info("knowledge_base_indexed", documents=indexed)
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {
        "status": "healthy" if check_db() else "degraded",
        "database": "up" if check_db() else "down",
        "mock_llm": settings.use_mock_llm,
    }


@app.post("/ask", response_model=QueryResponse, dependencies=[Depends(verify_api_key)])
def ask_question(request: QueryRequest, db: Session = Depends(get_db)):
    start = time.time()
    try:
        context = rag_engine.retrieve_context(request.question)
        answer = rag_engine.generate_answer(request.question, context)
        grounding = validation_service.check_grounding(answer, context)
        safe = validation_service.check_safety(answer)
        verified = grounding and safe
        confidence_score = int(grounding) * 70 + int(safe) * 30
        sources = [c[:120] + "..." if len(c) > 120 else c for c in context]

        db.add(
            InteractionLog(
                query=request.question,
                response=answer,
                sources_used=" | ".join(sources),
                confidence_score=confidence_score,
            )
        )
        db.commit()

        logger.info(
            "query_answered",
            verified=verified,
            confidence=confidence_score,
            duration=round(time.time() - start, 3),
        )
        return QueryResponse(
            answer=answer,
            sources=sources,
            verified=verified,
            confidence_score=confidence_score,
        )
    except Exception as exc:
        logger.exception("ask_failed", error=str(exc))
        raise HTTPException(status_code=500, detail="Failed to process question") from exc


@app.post("/admin/reindex", dependencies=[Depends(verify_api_key)])
def reindex_knowledge_base():
    count = rag_engine.index_markdown_folder()
    return {"status": "ok", "documents_indexed": count}

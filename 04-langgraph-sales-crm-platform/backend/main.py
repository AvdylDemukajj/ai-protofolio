"""FastAPI application for the LangGraph sales CRM agent."""

from __future__ import annotations

import uuid
from typing import List, Optional

import structlog
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import check_db_connection, get_db
from backend.graph.workflow import agent_graph
from backend.models import AgentRunResponse, LeadCreate, LeadResponse
from backend.services.crm_repository import (
    approve_draft,
    create_lead,
    get_lead,
    lead_to_dict,
    list_leads,
    reject_lead,
    save_agent_result,
)
from backend.services.notification import send_slack_notification

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ]
)
logger = structlog.get_logger(__name__)

app = FastAPI(
    title="LangGraph Sales CRM API",
    version="2.0.0",
    description="Autonomous B2B lead research, scoring, and outreach drafting with human-in-the-loop approval.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    if settings.API_KEY and x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


@app.get("/health")
def health_check():
    db_ok = check_db_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "up" if db_ok else "down",
        "environment": settings.ENVIRONMENT,
        "mock_llm": settings.use_mock_llm,
    }


@app.post("/leads/", response_model=AgentRunResponse, dependencies=[Depends(verify_api_key)])
async def create_and_process_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    """Create a lead, run the LangGraph agent, and persist results."""
    record = create_lead(db, lead)
    lead_id = str(record.id)

    initial_state = {
        "lead_id": lead_id,
        "company_info": lead.model_dump(),
        "messages": [],
        "analysis": None,
        "draft": None,
        "decision": None,
        "error": None,
        "research_iterations": 0,
    }

    try:
        result = agent_graph.invoke(initial_state)
    except Exception as exc:
        logger.exception("agent_failed", lead_id=lead_id)
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {exc}") from exc

    updated = save_agent_result(
        db,
        record.id,
        result.get("analysis"),
        result.get("draft"),
        result.get("decision"),
    )

    decision = result.get("decision")
    if updated.status == "pending_review" and updated.lead_score and updated.lead_score >= 70:
        send_slack_notification(
            f"🔥 Lead ready for review: {updated.company_name} (score {updated.lead_score})"
        )

    return AgentRunResponse(
        status="success",
        lead_id=updated.id,
        lead=LeadResponse(**lead_to_dict(updated)),
        agent_messages=result.get("messages", []),
        decision=decision.action if decision else None,
    )


@app.get("/leads/", response_model=List[LeadResponse], dependencies=[Depends(verify_api_key)])
def get_leads(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    records = list_leads(db, status=status, limit=limit)
    return [LeadResponse(**lead_to_dict(r)) for r in records]


@app.get("/leads/{lead_id}", response_model=LeadResponse, dependencies=[Depends(verify_api_key)])
def get_lead_by_id(lead_id: uuid.UUID, db: Session = Depends(get_db)):
    record = get_lead(db, lead_id)
    if not record:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse(**lead_to_dict(record))


@app.post("/leads/{lead_id}/approve", response_model=LeadResponse, dependencies=[Depends(verify_api_key)])
def approve_lead_draft(lead_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        record = approve_draft(db, lead_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    send_slack_notification(f"✅ Lead approved: {record.company_name}")
    return LeadResponse(**lead_to_dict(record))


@app.post("/leads/{lead_id}/reject", response_model=LeadResponse, dependencies=[Depends(verify_api_key)])
def reject_lead_draft(
    lead_id: uuid.UUID,
    reason: str = Query("Rejected by reviewer"),
    db: Session = Depends(get_db),
):
    try:
        record = reject_lead(db, lead_id, reason=reason)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return LeadResponse(**lead_to_dict(record))

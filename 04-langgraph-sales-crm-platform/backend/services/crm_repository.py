"""CRM persistence layer using SQLAlchemy."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

import structlog
from sqlalchemy.orm import Session

from backend.db_models import AgentAuditLogORM, InteractionORM, LeadORM
from backend.models import AgentDecision, LeadAnalysis, LeadCreate, OutreachDraft

logger = structlog.get_logger(__name__)


def create_lead(db: Session, payload: LeadCreate) -> LeadORM:
    lead = LeadORM(
        id=uuid.uuid4(),
        company_name=payload.company_name,
        website_url=payload.website_url,
        contact_email=str(payload.contact_email) if payload.contact_email else None,
        industry=payload.industry,
        employee_count=payload.employee_count,
        status="processing",
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def save_agent_result(
    db: Session,
    lead_id: uuid.UUID,
    analysis: LeadAnalysis | None,
    draft: OutreachDraft | None,
    decision: AgentDecision | None,
) -> LeadORM:
    lead = db.query(LeadORM).filter(LeadORM.id == lead_id).first()
    if not lead:
        raise ValueError(f"Lead {lead_id} not found")

    if analysis:
        lead.pain_points = analysis.pain_points
        lead.lead_score = analysis.lead_score
        lead.buying_intent = analysis.buying_intent
        lead.outreach_strategy = analysis.outreach_strategy
        lead.confidence_score = analysis.confidence

    if draft:
        lead.draft_subject = draft.subject
        lead.draft_body = draft.body
        lead.requires_human_review = draft.requires_human_review
        lead.status = "pending_review"
        db.add(
            InteractionORM(
                lead_id=lead.id,
                interaction_type="email_draft",
                content=f"Subject: {draft.subject}\n\n{draft.body}",
                ai_generated=True,
                human_approved=False,
            )
        )
    elif decision and decision.action == "reject":
        lead.status = "rejected"
    else:
        lead.status = "qualified"

    if decision:
        lead.agent_decision = decision.action
        db.add(
            AgentAuditLogORM(
                lead_id=lead.id,
                action_taken=decision.action,
                reasoning=decision.reasoning,
                confidence_score=analysis.confidence if analysis else None,
            )
        )

    lead.last_interaction_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(lead)
    logger.info("lead_saved", lead_id=str(lead_id), status=lead.status)
    return lead


def list_leads(db: Session, status: str | None = None, limit: int = 50) -> list[LeadORM]:
    query = db.query(LeadORM).order_by(LeadORM.created_at.desc())
    if status:
        query = query.filter(LeadORM.status == status)
    return query.limit(limit).all()


def get_lead(db: Session, lead_id: uuid.UUID) -> LeadORM | None:
    return db.query(LeadORM).filter(LeadORM.id == lead_id).first()


def approve_draft(db: Session, lead_id: uuid.UUID) -> LeadORM:
    lead = get_lead(db, lead_id)
    if not lead:
        raise ValueError("Lead not found")
    lead.status = "approved"
    lead.requires_human_review = False
    for interaction in lead.interactions:
        if interaction.interaction_type == "email_draft":
            interaction.human_approved = True
    lead.last_interaction_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(lead)
    return lead


def reject_lead(db: Session, lead_id: uuid.UUID, reason: str = "Human rejected") -> LeadORM:
    lead = get_lead(db, lead_id)
    if not lead:
        raise ValueError("Lead not found")
    lead.status = "rejected"
    lead.agent_decision = "human_reject"
    db.add(
        AgentAuditLogORM(
            lead_id=lead.id,
            action_taken="human_reject",
            reasoning=reason,
        )
    )
    db.commit()
    db.refresh(lead)
    return lead


def lead_to_dict(lead: LeadORM) -> dict[str, Any]:
    return {
        "id": str(lead.id),
        "company_name": lead.company_name,
        "website_url": lead.website_url,
        "contact_email": lead.contact_email,
        "industry": lead.industry,
        "employee_count": lead.employee_count,
        "pain_points": lead.pain_points or [],
        "lead_score": lead.lead_score,
        "buying_intent": lead.buying_intent,
        "outreach_strategy": lead.outreach_strategy,
        "status": lead.status,
        "draft_subject": lead.draft_subject,
        "draft_body": lead.draft_body,
        "requires_human_review": lead.requires_human_review,
        "agent_decision": lead.agent_decision,
        "confidence_score": float(lead.confidence_score) if lead.confidence_score else None,
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
    }

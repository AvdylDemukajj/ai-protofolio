"""LangGraph node implementations for the sales outreach agent."""

from __future__ import annotations

import json
import re

import structlog
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from backend.config import settings
from backend.graph.state import AgentState
from backend.models import AgentDecision, LeadAnalysis, OutreachDraft

logger = structlog.get_logger(__name__)


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=0.2,
        api_key=settings.OPENAI_API_KEY or "not-set",
    )


def _parse_json_block(text: str) -> dict:
    cleaned = re.sub(r"```json|```", "", text).strip()
    return json.loads(cleaned)


def research_node(state: AgentState) -> dict:
    """Research company context and produce structured lead analysis."""
    company = state["company_info"]
    company_name = company.get("company_name", "Unknown")
    industry = company.get("industry", "General B2B")
    iterations = state.get("research_iterations", 0) + 1

    if settings.use_mock_llm:
        analysis = LeadAnalysis(
            pain_points=["Manual sales workflows", "Low outbound conversion", "Slow lead qualification"],
            lead_score=85 if (company.get("employee_count") or 0) >= 50 else 55,
            buying_intent="warm",
            outreach_strategy="Lead with automation ROI and time-to-value.",
            confidence=0.88,
        )
        logger.info("research_mock", company=company_name, score=analysis.lead_score)
        return {
            "analysis": analysis,
            "research_iterations": iterations,
            "messages": [f"Research completed for {company_name} (mock)."],
        }

    llm = _get_llm()
    prompt = f"""Analyze this B2B lead for sales outreach potential.
Company: {company_name}
Industry: {industry}
Website: {company.get('website_url', 'N/A')}
Employees: {company.get('employee_count', 'unknown')}

Return JSON only:
{{
  "pain_points": ["..."],
  "lead_score": 0-100,
  "buying_intent": "cold" | "warm" | "hot",
  "outreach_strategy": "one sentence strategy",
  "confidence": 0.0-1.0
}}"""
    try:
        response = llm.invoke(
            [
                SystemMessage(content="You are a B2B sales research analyst. Output valid JSON only."),
                HumanMessage(content=prompt),
            ]
        )
        data = _parse_json_block(response.content)
        analysis = LeadAnalysis(**data)
    except Exception as exc:
        logger.warning("research_llm_failed", error=str(exc))
        analysis = LeadAnalysis(
            pain_points=["Unable to complete deep research"],
            lead_score=50,
            buying_intent="cold",
            outreach_strategy="Request discovery call to learn more.",
            confidence=0.4,
        )

    return {
        "analysis": analysis,
        "research_iterations": iterations,
        "messages": [f"Research completed for {company_name}."],
    }


def strategy_node(state: AgentState) -> dict:
    """Decide next action based on analysis and iteration limits."""
    analysis = state.get("analysis")
    if not analysis:
        return {
            "decision": AgentDecision(
                action="research",
                reasoning="Analysis missing; run research first.",
                risk_level="low",
            ),
            "messages": ["Strategy: research required."],
        }

    score = analysis.lead_score
    iterations = state.get("research_iterations", 0)
    max_iter = settings.MAX_RESEARCH_ITERATIONS

    if score < 40:
        action = "reject"
        reasoning = f"Lead score {score} below qualification threshold."
        risk = "low"
    elif score < 70 and iterations < max_iter:
        action = "research"
        reasoning = f"Score {score} is moderate; additional research allowed ({iterations}/{max_iter})."
        risk = "low"
    elif score >= 70:
        action = "draft_email"
        reasoning = f"Strong score ({score}) — proceed to personalized outreach draft."
        risk = "medium" if analysis.confidence < 0.7 else "low"
    else:
        action = "reject"
        reasoning = f"Score {score} after max research iterations."
        risk = "low"

    return {
        "decision": AgentDecision(action=action, reasoning=reasoning, risk_level=risk),
        "messages": [f"Strategy: {action} — {reasoning}"],
    }


def draft_node(state: AgentState) -> dict:
    """Generate a human-review outreach email draft."""
    analysis = state["analysis"]
    company_name = state["company_info"].get("company_name", "there")

    if settings.use_mock_llm:
        draft = OutreachDraft(
            subject=f"Streamlining operations at {company_name}",
            body=(
                f"Hi team at {company_name},\n\n"
                f"We help companies address {analysis.pain_points[0].lower()} with measurable ROI. "
                f"{analysis.outreach_strategy}\n\n"
                "Would you be open to a 15-minute call this week?\n\nBest regards,\nSales Team"
            ),
            tone="professional",
            requires_human_review=True,
        )
        return {"draft": draft, "messages": ["Draft email generated (mock)."]}

    llm = _get_llm()
    prompt = f"""Write a B2B sales email draft.
Company: {company_name}
Pain points: {', '.join(analysis.pain_points)}
Strategy: {analysis.outreach_strategy}
Tone: professional, concise, no hype.

Return JSON only:
{{
  "subject": "...",
  "body": "...",
  "tone": "professional",
  "requires_human_review": true
}}"""
    try:
        response = llm.invoke(
            [
                SystemMessage(content="You are a senior B2B copywriter. Output valid JSON only."),
                HumanMessage(content=prompt),
            ]
        )
        data = _parse_json_block(response.content)
        draft = OutreachDraft(**data)
    except Exception as exc:
        logger.warning("draft_llm_failed", error=str(exc))
        draft = OutreachDraft(
            subject=f"Introduction — {company_name}",
            body=f"Hi {company_name} team,\n\nWe would like to explore how we can help with {analysis.pain_points[0]}.\n\nBest,\nSales",
            requires_human_review=True,
        )

    return {"draft": draft, "messages": ["Draft email generated."]}

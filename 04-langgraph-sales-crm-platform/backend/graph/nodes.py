from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from backend.models import LeadAnalysis, OutreachDraft, AgentDecision
from backend.graph.state import AgentState
from backend.config import settings
import json

# Initialize LLM (Mock fallback if no key provided for demo stability)
llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0, api_key=settings.OPENAI_API_KEY or "sk-fake")

def research_node(state: AgentState) -> AgentState:
    """Simulates researching a company to find pain points."""
    # In production, this would call a Search API or scrape the website
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a B2B Researcher. Identify 3 likely pain points for {company} in the {industry} sector."),
        ("human", "Company: {company_info}")
    ])
    # Mocking response for demo reliability without external API calls
    mock_analysis = {
        "pain_points": ["High operational costs", "Manual data entry errors", "Slow customer support"],
        "lead_score": 85,
        "buying_intent": "warm",
        "outreach_strategy": "Focus on ROI and automation efficiency.",
        "confidence": 0.88
    }
    return {"analysis": LeadAnalysis(**mock_analysis), "messages": ["Research completed."]}

def strategy_node(state: AgentState) -> AgentState:
    """Decides the next action based on analysis."""
    score = state["analysis"].lead_score if state.get("analysis") else 0
    
    if score > 70:
        action = "draft_email"
        reasoning = f"High score ({score}) indicates strong potential."
        risk = "medium"
    elif score > 40:
        action = "research"
        reasoning = "Moderate score, need more data."
        risk = "low"
    else:
        action = "reject"
        reasoning = "Low score, not a good fit."
        risk = "low"

    return {
        "decision": AgentDecision(action=action, reasoning=reasoning, risk_level=risk),
        "messages": [f"Strategy decided: {action}"]
    }

def draft_node(state: AgentState) -> AgentState:
    """Drafts a personalized email."""
    analysis = state["analysis"]
    prompt_text = f"""
    Draft a concise, value-driven email to {state['company_info'].get('company_name', 'Customer')}.
    Pain Points: {', '.join(analysis.pain_points)}
    Strategy: {analysis.outreach_strategy}
    Tone: Professional yet engaging.
    """
    
    # Mocking draft generation for demo stability
    mock_draft = {
        "subject": f"Optimizing {state['company_info'].get('company_name', '')}'s operations",
        "body": f"Hi Team,\n\nI noticed challenges with {analysis.pain_points[0]}. Our solution helps companies like yours reduce costs by 20%.\n\nBest,\nSales Team",
        "tone": "professional",
        "requires_human_review": True
    }
    
    return {"draft": OutreachDraft(**mock_draft), "messages": ["Draft generated."]}
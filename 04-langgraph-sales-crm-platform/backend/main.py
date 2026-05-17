from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import LeadCreate, LeadResponse, LeadStatus
from backend.graph.workflow import app as agent_graph
from backend.services.crm_repository import save_lead_result
from backend.services.notification import send_slack_notification
import uuid

app = FastAPI(title="Sales CRM Agent API")

@app.post("/leads/", response_model=dict)
async def create_and_process_lead(lead: LeadCreate):
    """Creates a lead and triggers the AI Agent."""
    lead_id = str(uuid.uuid4())
    
    # Initial State for Agent
    initial_state = {
        "lead_id": lead_id,
        "company_info": lead.dict(),
        "messages": [],
        "analysis": None,
        "draft_email": None,
        "decision": None,
        "error": None
    }
    
    try:
        # Run Agent
        result = agent_graph.invoke(initial_state)
        
        # Save Results to DB
        if result.get('analysis'):
            save_lead_result(
                lead_id, 
                result['analysis'], 
                result.get('draft_email', ''), 
                result.get('decision', '')
            )
        
        # Notify if high priority
        if result.get('decision') == 'send_for_review':
            send_slack_notification(f"New qualified lead: {lead.company_name}")
            
        return {"status": "success", "lead_id": lead_id, "agent_result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}
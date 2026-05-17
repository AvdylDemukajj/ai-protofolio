from sqlalchemy.orm import Session
from backend.models import SupportTicket
from backend.database import SessionLocal
from backend.utils.logger import logger
from typing import Optional

def get_ticket_status(ticket_id: str) -> str:
    """Retrieves the current status of a support ticket."""
    db = SessionLocal()
    try:
        ticket = db.query(SupportTicket).filter(SupportTicket.ticket_id_str == ticket_id).first()
        if not ticket:
            return "Ticket not found."
        return f"Ticket {ticket_id} is currently '{ticket.status}' (Priority: {ticket.priority})."
    finally:
        db.close()

def update_ticket_status(ticket_id: str, new_status: str, reason: str) -> str:
    """Updates the status of a support ticket. Requires justification."""
    db = SessionLocal()
    try:
        ticket = db.query(SupportTicket).filter(SupportTicket.ticket_id_str == ticket_id).first()
        if not ticket:
            return "Error: Ticket not found."
        
        old_status = ticket.status
        ticket.status = new_status
        db.commit()
        
        logger.info("Ticket status updated", ticket=ticket_id, old=old_status, new=new_status, reason=reason)
        return f"Successfully updated ticket {ticket_id} from '{old_status}' to '{new_status}'."
    except Exception as e:
        db.rollback()
        return f"Failed to update ticket: {str(e)}"
    finally:
        db.close()

def assign_ticket(ticket_id: str, agent_name: str) -> str:
    """Assigns a ticket to a specific human agent."""
    db = SessionLocal()
    try:
        ticket = db.query(SupportTicket).filter(SupportTicket.ticket_id_str == ticket_id).first()
        if not ticket:
            return "Error: Ticket not found."
        
        ticket.assigned_to = agent_name
        db.commit()
        return f"Ticket {ticket_id} assigned to {agent_name}."
    except Exception as e:
        db.rollback()
        return f"Failed to assign ticket: {str(e)}"
    finally:
        db.close()
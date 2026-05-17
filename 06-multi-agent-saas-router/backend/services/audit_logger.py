from backend.database import SessionLocal
from backend.models import AuditLog
import structlog

logger = structlog.get_logger()

async def log_agent_action(agent_name: str, action_type: str, input_summary: str, output_summary: str, confidence: int, policy_checks_passed: bool):
    db = SessionLocal()
    try:
        log_entry = AuditLog(
            agent_name=agent_name,
            action_type=action_type,
            input_summary=input_summary,
            output_summary=output_summary,
            confidence_score=confidence,
            policy_checks_passed=policy_checks_passed
        )
        db.add(log_entry)
        db.commit()
        logger.info("Audit log created", agent=agent_name, passed=policy_checks_passed)
    except Exception as e:
        logger.error("Failed to log audit", error=str(e))
        db.rollback()
    finally:
        db.close()
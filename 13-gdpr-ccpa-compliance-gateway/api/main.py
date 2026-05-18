from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.saga_orchestrator import SagaOrchestrator
import structlog

logger = structlog.get_logger()
app = FastAPI(title="GDPR Compliance Gateway", version="1.0.0")

class DeletionRequest(BaseModel):
    user_id: str
    reason: str = "user_request" # user_request, legal_obligation

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/privacy/delete-user")
async def delete_user(request: DeletionRequest):
    logger.info("Received GDPR Deletion Request", user_id=request.user_id)
    
    try:
        orchestrator = SagaOrchestrator(request.user_id)
        result = await orchestrator.execute_deletion()
        return result
    except Exception as e:
        logger.error("Deletion process failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
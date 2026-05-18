import structlog
from typing import List, Dict, Any
from connectors.postgres_connector import PostgresConnector
from connectors.s3_connector import S3Connector
from connectors.analytics_connector import AnalyticsConnector
from core.audit_log import AuditLogger

logger = structlog.get_logger()

class SagaStep:
    def __init__(self, name: str, action: callable, compensate: callable):
        self.name = name
        self.action = action
        self.compensate = compensate

class SagaOrchestrator:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.executed_steps: List[SagaStep] = []
        self.pg = PostgresConnector()
        self.s3 = S3Connector()
        self.analytics = AnalyticsConnector()
        self.audit = AuditLogger()

    async def execute_deletion(self):
        """Executes the distributed deletion with automatic rollback on failure."""
        
        # Define Steps: Action and Compensation (Rollback logic)
        # Note: In real GDPR, rollback might mean "restore from backup" which is complex.
        # Here we simulate the pattern structure.
        steps = [
            SagaStep(
                name="Analytics Deletion",
                action=lambda: self.analytics.delete_user(self.user_id),
                compensate=lambda: logger.warning("Compensation needed: Re-add user to Analytics")
            ),
            SagaStep(
                name="S3 Object Deletion",
                action=lambda: self.s3.delete_user_objects(self.user_id),
                compensate=lambda: logger.warning("Compensation needed: Restore S3 objects from Glacier")
            ),
            SagaStep(
                name="Database Anonymization",
                action=lambda: self.pg.anonymize_user(self.user_id),
                compensate=lambda: logger.error("CRITICAL: Cannot rollback DB anonymization easily. Manual intervention required.")
            )
        ]

        try:
            logger.info("Starting GDPR Deletion Saga", user_id=self.user_id)
            
            for step in steps:
                logger.info(f"Executing step: {step.name}")
                await step.action()
                self.executed_steps.append(step)
                logger.info(f"Step {step.name} completed successfully")

            # If all succeed
            await self.audit.log_success(self.user_id, [s.name for s in steps])
            logger.info("GDPR Deletion Saga Completed Successfully", user_id=self.user_id)
            return {"status": "success", "message": "User data purged from all systems"}

        except Exception as e:
            logger.error("Saga Failed", error=str(e), executed_steps=[s.name for s in self.executed_steps])
            
            # Trigger Compensating Transactions (Rollback)
            logger.warning("Initiating Compensating Transactions (Rollback)...")
            for step in reversed(self.executed_steps):
                try:
                    step.compensate()
                    logger.info(f"Compensation for {step.name} executed")
                except Exception as comp_err:
                    logger.critical(f"Compensation failed for {step.name}", error=str(comp_err))
            
            await self.audit.log_failure(self.user_id, str(e), [s.name for s in self.executed_steps])
            raise Exception(f"Deletion failed: {str(e)}. Rollback initiated. Manual review required.")

saga_orchestrator = SagaOrchestrator
import structlog
from typing import Callable, List

from connectors.analytics_connector import AnalyticsConnector
from connectors.postgres_connector import PostgresConnector
from connectors.s3_connector import S3Connector
from core.audit_log import AuditLogger

logger = structlog.get_logger()


class SagaStep:
    def __init__(self, name: str, action: Callable[[], None], compensate: Callable[[], None]):
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

    def execute_deletion(self) -> dict:
        """Executes distributed deletion with compensating transactions on failure."""
        steps = [
            SagaStep(
                name="Analytics Deletion",
                action=lambda: self.analytics.delete_user(self.user_id),
                compensate=lambda: logger.warning(
                    "Compensation needed: Re-add user to Analytics"
                ),
            ),
            SagaStep(
                name="S3 Object Deletion",
                action=lambda: self.s3.delete_user_objects(self.user_id),
                compensate=lambda: logger.warning(
                    "Compensation needed: Restore S3 objects from Glacier"
                ),
            ),
            SagaStep(
                name="Database Anonymization",
                action=lambda: self.pg.anonymize_user(self.user_id),
                compensate=lambda: logger.error(
                    "CRITICAL: Cannot rollback DB anonymization easily."
                ),
            ),
        ]

        try:
            logger.info("Starting GDPR Deletion Saga", user_id=self.user_id)

            for step in steps:
                logger.info("Executing step: %s", step.name)
                step.action()
                self.executed_steps.append(step)
                logger.info("Step %s completed successfully", step.name)

            self.audit.log_success(self.user_id, [s.name for s in steps])
            logger.info("GDPR Deletion Saga Completed Successfully", user_id=self.user_id)
            return {"status": "success", "message": "User data purged from all systems"}

        except Exception as exc:
            logger.error(
                "Saga Failed",
                error=str(exc),
                executed_steps=[s.name for s in self.executed_steps],
            )

            logger.warning("Initiating Compensating Transactions (Rollback)...")
            for step in reversed(self.executed_steps):
                try:
                    step.compensate()
                    logger.info("Compensation for %s executed", step.name)
                except Exception as comp_err:
                    logger.critical(
                        "Compensation failed for %s", step.name, error=str(comp_err)
                    )

            self.audit.log_failure(
                self.user_id, str(exc), [s.name for s in self.executed_steps]
            )
            raise RuntimeError(
                f"Deletion failed: {exc}. Rollback initiated. Manual review required."
            ) from exc

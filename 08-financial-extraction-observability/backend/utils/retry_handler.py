import redis
import json
import time
from backend.config import settings
import structlog

logger = structlog.get_logger()

class RetryHandler:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.queue_name = "document_processing_queue"
        self.dlq_name = "document_dead_letter_queue"

    def add_to_queue(self, task_data: dict):
        self.redis.lpush(self.queue_name, json.dumps(task_data))
        logger.info(f"Task added to queue: {task_data.get('doc_id')}")

    def retry_task(self, task_data: dict):
        retries = task_data.get("retries", 0)
        if retries < settings.MAX_RETRIES:
            task_data["retries"] = retries + 1
            logger.warning(f"Retrying task {task_data.get('doc_id')}, attempt {task_data['retries']}")
            # Add delay logic here in prod (e.g., delayed queues)
            time.sleep(settings.RETRY_DELAY_SECONDS)
            self.redis.lpush(self.queue_name, json.dumps(task_data))
        else:
            logger.error(f"Task {task_data.get('doc_id')} failed max retries. Moving to DLQ.")
            self.move_to_dlq(task_data)

    def move_to_dlq(self, task_data: dict):
        task_data["failed_at"] = time.time()
        self.redis.lpush(self.dlq_name, json.dumps(task_data))
        # Update DB status to DEAD_LETTER (handled in worker)

retry_handler = None # Initialized in worker
from prometheus_client import Counter, Histogram, Gauge
import time

# Counters
PROCESSING_TOTAL = Counter('doc_processing_total', 'Total documents processed', ['status'])
PROCESSING_TIME = Histogram('doc_processing_seconds', 'Time spent processing document')

# Gauges
QUEUE_SIZE = Gauge('queue_size', 'Current size of the processing queue')

def track_processing(status: str):
    PROCESSING_TOTAL.labels(status=status).inc()

def start_timer():
    return time.time()

def stop_timer(start_time: float):
    PROCESSING_TIME.observe(time.time() - start_time)
import os, json, structlog
from confluent_kafka import Consumer
from sklearn.ensemble import IsolationForest
import numpy as np

logger = structlog.get_logger()
model = IsolationForest()
model.fit(np.random.rand(100, 3))

def start():
    c = Consumer({'bootstrap.servers': 'kafka:29092', 'group.id': 'fraud-v2'})
    c.subscribe(['transactions-topic'])
    while True:
        m = c.poll(1.0)
        if m and not m.error():
            tx = json.loads(m.value().decode())
            logger.info("Processed", tx_id=tx.get('id'))
if __name__ == "__main__": start()
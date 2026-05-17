import os
import json
import time
import structlog
from confluent_kafka import Consumer, KafkaException
from psycopg2 import connect
from stream_processor.rules_engine import RulesEngine
from stream_processor.ml_model import FraudModel
from stream_processor.alert_service import AlertService
import redis

logger = structlog.get_logger()

def process_message(msg):
    try:
        tx = json.loads(msg.value().decode('utf-8'))
        tx_id = tx['transaction_id']
        user_id = tx['user_id']
        amount = tx['amount']
        
        # Init Services
        r = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'))
        rules_engine = RulesEngine(r)
        ml_model = FraudModel() # Loads pre-trained model
        alert_service = AlertService(os.getenv('DB_URL'))

        # 1. Rule Engine Checks (Fast, Deterministic)
        rule_flags = []
        if rules_engine.check_velocity(user_id):
            rule_flags.append("VELOCITY_EXCEEDED")
        if rules_engine.check_amount_threshold(amount):
            rule_flags.append("HIGH_AMOUNT")

        # 2. ML Model Check (Probabilistic)
        # Features: amount, hour, velocity_count
        velocity_count = int(r.get(f"user:{user_id}:vel") or 0)
        features = {
            'amount': amount,
            'hour': time.localtime().tm_hour,
            'velocity': velocity_count
        }
        ml_risk = ml_model.predict(features)

        # 3. Decision Logic
        final_score = ml_risk
        status = 'approved'
        
        if len(rule_flags) > 0 or ml_risk > 0.7:
            status = 'rejected' if ml_risk > 0.9 else 'flagged'
            
            # Create Alert
            alert_service.create_alert(
                tx_id=tx_id,
                reason_code=",".join(rule_flags) if rule_flags else "ML_HIGH_RISK",
                details={'ml_score': ml_risk, 'rules': rule_flags}
            )
            logger.warning("Fraud Detected", tx_id=tx_id, score=final_score, status=status)
        else:
            logger.info("Transaction Approved", tx_id=tx_id)

        # 4. Update Transaction Status in DB (Async in prod, sync here for demo)
        alert_service.update_transaction_status(tx_id, status, final_score)

    except Exception as e:
        logger.error("Processing failed", error=str(e))

def start_consumer():
    conf = {
        'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092'),
        'group.id': 'fraud-detection-group-v2',
        'auto.offset.reset': 'earliest'
    }
    
    consumer = Consumer(conf)
    consumer.subscribe(['transactions-topic'])
    
    logger.info("🚀 Fraud Detection Engine Started. Listening...")
    
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None: continue
            if msg.error():
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())
            
            process_message(msg)
    finally:
        consumer.close()

if __name__ == "__main__":
    start_consumer()
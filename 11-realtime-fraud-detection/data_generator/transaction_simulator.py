from confluent_kafka import Producer
import json
import time
import random
import uuid
from datetime import datetime

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')

def generate_transactions():
    conf = {'bootstrap.servers': 'kafka:29092'}
    producer = Producer(conf)
    
    users = [f"user_{i}" for i in range(50)]
    
    print("🚀 Starting Transaction Simulation...")
    
    i = 0
    while True:
        user = random.choice(users)
        # 5% chance of fraud pattern (high amount or high velocity simulation)
        is_fraud = random.random() < 0.05
        
        amount = round(random.uniform(10, 200) if not is_fraud else random.uniform(3000, 10000), 2)
        
        tx = {
            "transaction_id": str(uuid.uuid4()),
            "user_id": user,
            "amount": amount,
            "currency": "USD",
            "merchant": "OnlineStore",
            "timestamp": datetime.now().isoformat()
        }
        
        producer.produce('transactions-topic', json.dumps(tx), callback=delivery_report)
        producer.poll(0)
        
        if i % 100 == 0:
            print(f"Sent {i} transactions...")
            
        time.sleep(0.5) # Adjust speed
        i += 1

if __name__ == "__main__":
    generate_transactions()
import requests
import random
from datetime import date, timedelta

BACKEND_URL = "http://localhost:8000"

def seed_data():
    print("🌱 Seeding Demo Data...")
    vendors = ["TechCorp", "Global Logistics", "Office Supplies"]
    for i in range(10):
        # Mocking an upload would require a real file, so we simulate DB insertion logic here if needed
        # For this script, we just print what would happen
        print(f"   - Simulated invoice from {random.choice(vendors)}")
    print("✅ Seeding complete (Mock).")

if __name__ == "__main__":
    seed_data()
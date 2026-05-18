"""Smoke test API health and optional lead creation."""

import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
API_KEY = os.getenv("API_KEY", "")


def main() -> None:
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    try:
        health = httpx.get(f"{API_URL}/health", timeout=10)
        health.raise_for_status()
        print(f"Health: {health.json()}")
    except Exception as exc:
        print(f"Health check failed: {exc}")
        sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == "--create-lead":
        payload = {
            "company_name": "API Test Corp",
            "industry": "Technology",
            "employee_count": 200,
            "contact_email": "cto@apitest.io",
        }
        resp = httpx.post(f"{API_URL}/leads/", json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        print(f"Lead created: {resp.json()['lead_id']}")

    print("Validation complete.")


if __name__ == "__main__":
    main()

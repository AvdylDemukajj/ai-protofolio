import hmac
import hashlib
import os

def verify_signature(payload: str, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

def hash_sensitive_data(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()
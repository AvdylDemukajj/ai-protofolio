import hashlib
import os

def generate_pseudonym(user_id: str) -> str:
    """Generates a deterministic but irreversible pseudonym."""
    salt = os.getenv("GDPR_SALT", "default_salt_change_me")
    hash_obj = hashlib.sha256((user_id + salt).encode())
    return f"user_{hash_obj.hexdigest()[:16]}"

def anonymize_email(email: str) -> str:
    """Replaces email with a redacted version."""
    if "@" not in email:
        return "unknown@example.com"
    parts = email.split("@")
    return f"{parts[0][:2]}***@{parts[1]}"
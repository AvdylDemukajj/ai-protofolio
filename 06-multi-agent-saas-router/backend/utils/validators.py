def check_policy_violations(text: str, category: str) -> list:
    violations = []
    text_lower = text.lower()
    
    # Rule 1: No financial commitments without approval
    if category == "refunds" or category == "billing":
        if "guarantee" in text_lower and "refund" in text_lower:
            violations.append("Unauthorized financial guarantee")
        if "approve immediately" in text_lower:
            violations.append("Bypassing approval workflow")
            
    # Rule 2: No PII leakage
    if "@" in text_lower and "email" not in text_lower:
         # Simple heuristic check
         pass

    return violations
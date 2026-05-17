from backend.config import settings
from backend.utils.logger import logger

class SafetyGuard:
    @staticmethod
    def check_destructive_action(tool_name: str, args: dict) -> bool:
        """
        Returns True if the action is blocked.
        Blocks destructive actions if ALLOW_DESTRUCTIVE_ACTIONS is False.
        """
        # List of sensitive tools
        sensitive_tools = ["update_ticket_status", "assign_ticket", "delete_ticket"]
        
        if tool_name in sensitive_tools:
            if not settings.ALLOW_DESTRUCTIVE_ACTIONS:
                logger.warning("BLOCKED DESTRUCTIVE ACTION", tool=tool_name, args=args)
                return True # Block it
            
            # Additional logic: Prevent closing high priority tickets without human review
            if tool_name == "update_ticket_status" and args.get("new_status") == "Closed":
                # In a real scenario, we'd check the ticket's priority first
                if "high" in str(args).lower():
                    logger.warning("BLOCKED HIGH PRIORITY CLOSE", args=args)
                    return True

        return False # Allow it

    @staticmethod
    def check_injection_attempt(text: str) -> bool:
        """Basic check for prompt injection patterns."""
        dangerous_phrases = ["ignore previous instructions", "system override", "delete all"]
        return any(phrase in text.lower() for phrase in dangerous_phrases)

safety_guard = SafetyGuard()
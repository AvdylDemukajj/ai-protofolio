import redis

class RulesEngine:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def check_velocity(self, user_id: str, window_seconds: int = 3600, max_count: int = 5) -> bool:
        """Checks if user made > max_count transactions in the last hour."""
        key = f"user:{user_id}:vel"
        current_count = self.redis.incr(key)
        
        # Set expiry only on first increment
        if current_count == 1:
            self.redis.expire(key, window_seconds)
        
        return current_count > max_count

    def check_amount_threshold(self, amount: float, threshold: float = 5000.0) -> bool:
        return amount > threshold
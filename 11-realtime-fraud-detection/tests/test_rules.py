import pytest
from unittest.mock import MagicMock
from stream_processor.rules_engine import RulesEngine

def test_velocity_check():
    mock_redis = MagicMock()
    mock_redis.incr.return_value = 6 # Simulate 6th transaction
    engine = RulesEngine(mock_redis)
    
    assert engine.check_velocity("user_123") == True

def test_amount_threshold():
    engine = RulesEngine(None)
    assert engine.check_amount_threshold(6000.0) == True
    assert engine.check_amount_threshold(100.0) == False
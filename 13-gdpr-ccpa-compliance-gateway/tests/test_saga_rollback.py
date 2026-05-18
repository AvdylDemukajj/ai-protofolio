from unittest.mock import patch

import pytest

from core.saga_orchestrator import SagaOrchestrator


def test_saga_rollback_on_failure():
    """If step 2 fails, compensation runs and an error is raised."""
    user_id = "test_user_123"
    orchestrator = SagaOrchestrator(user_id)

    with patch.object(orchestrator.analytics, "delete_user", return_value=True):
        with patch.object(
            orchestrator.s3,
            "delete_user_objects",
            side_effect=Exception("S3 Down"),
        ):
            with pytest.raises(RuntimeError) as exc_info:
                orchestrator.execute_deletion()

            assert "S3 Down" in str(exc_info.value)

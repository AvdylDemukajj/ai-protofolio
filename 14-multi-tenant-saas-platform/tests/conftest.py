import os
import sys
import uuid
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

SAMPLE_TENANT_ID = "00000000-0000-0000-0000-000000000001"
SAMPLE_SCHEMA = f"tenant_{SAMPLE_TENANT_ID.replace('-', '')[:8]}"


@pytest.fixture
def mock_db_connection():
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    with patch("psycopg2.connect", return_value=mock_conn):
        yield mock_conn, mock_cur


@pytest.fixture
def sample_tenant():
    return {
        "id": SAMPLE_TENANT_ID,
        "schema": SAMPLE_SCHEMA,
        "plan": "free",
        "active": True,
        "subdomain": "acme",
    }

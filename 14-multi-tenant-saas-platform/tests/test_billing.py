from unittest.mock import patch

import pytest

from billing_engine.invoice_generator import generate_monthly_invoice


@pytest.fixture
def mock_invoice_db():
    with patch("billing_engine.invoice_generator.psycopg2.connect") as mock_connect:
        mock_conn = mock_connect.return_value
        mock_cur = mock_conn.cursor.return_value
        mock_cur.fetchone.return_value = ("free",)
        mock_cur.fetchall.return_value = [
            ("api_call", 1000),
            ("storage_mb", 100),
        ]
        yield mock_cur


def test_billing_calculation_free_plan(mock_invoice_db):
    result = generate_monthly_invoice("00000000-0000-0000-0000-000000000000", 2023, 10)
    assert result["total"] == 6.0
    assert len(result["breakdown"]) >= 2


def test_billing_pro_plan_includes_quota(mock_invoice_db):
    mock_invoice_db.fetchone.return_value = ("pro",)
    mock_invoice_db.fetchall.return_value = [("api_call", 5000)]

    result = generate_monthly_invoice("00000000-0000-0000-0000-000000000001", 2023, 10)
    assert result["total"] == 29.0


@patch("billing_engine.usage_tracker.psycopg2.connect")
def test_log_usage_mock(mock_connect):
    from billing_engine.usage_tracker import log_usage

    mock_connect.return_value.cursor.return_value = mock_connect.return_value.cursor()
    log_usage("00000000-0000-0000-0000-000000000000", "api_call", 1)
    mock_connect.return_value.cursor.return_value.execute.assert_called()

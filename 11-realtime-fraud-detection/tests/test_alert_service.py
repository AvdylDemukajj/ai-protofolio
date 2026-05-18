from unittest.mock import MagicMock, patch

from stream_processor.alert_service import AlertService


@patch("stream_processor.alert_service.psycopg2.connect")
def test_insert_before_alert_flow(mock_connect):
    mock_conn = mock_connect.return_value
    mock_cur = mock_conn.cursor.return_value
    mock_cur.fetchone.side_effect = [("uuid-1",), ("uuid-1",)]

    service = AlertService("postgresql://test")
    tx_uuid = service.insert_transaction("tx-1", "user-1", 5000.0)
    assert tx_uuid == "uuid-1"

    service.create_alert("tx-1", "HIGH_AMOUNT", {"ml_score": 0.9})
    assert mock_cur.execute.call_count >= 2

    insert_sql = mock_cur.execute.call_args_list[0][0][0]
    assert "INSERT INTO transactions" in insert_sql

import os
import uuid
from unittest.mock import MagicMock, patch

import pytest

from onboarding.provision_tenant import onboard_new_tenant

MASTER_DB_URL = os.getenv(
    "MASTER_DB_URL",
    "postgresql://saas_admin:SecureRootPass123!@localhost:5434/master_db",
)


def _schema_name_for_subdomain(subdomain: str) -> str:
    """Matches dynamic schema naming from provision_tenant."""
    tenant_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"test-{subdomain}")
    return f"tenant_{tenant_id.hex[:8]}"


@pytest.mark.integration
@pytest.mark.skip(reason="Requires live PostgreSQL on port 5434")
def test_data_isolation_live():
    """Verifies tenant schemas use distinct search_path contexts (requires running Postgres)."""
    try:
        import psycopg2
    except ImportError:
        pytest.skip("psycopg2 not available")

    schema_a = _schema_name_for_subdomain("acme-test")
    schema_b = _schema_name_for_subdomain("stark-test")

    conn = psycopg2.connect(MASTER_DB_URL)
    cur = conn.cursor()

    for schema in (schema_a, schema_b):
        cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS "{schema}".data (
                id SERIAL PRIMARY KEY,
                content TEXT
            )
            """
        )
    conn.commit()

    cur.execute(f'SET search_path TO "{schema_a}"')
    cur.execute("DELETE FROM data")
    cur.execute("INSERT INTO data (content) VALUES (%s)", ("Secret Data A",))
    conn.commit()

    cur.execute(f'SET search_path TO "{schema_b}"')
    cur.execute("SELECT content FROM data")
    rows = cur.fetchall()
    assert all("Secret Data A" not in str(row) for row in rows)

    cur.close()
    conn.close()


@patch("onboarding.provision_tenant.psycopg2.connect")
def test_onboarding_uses_dynamic_schema(mock_connect):
    mock_conn = mock_connect.return_value
    mock_cur = mock_conn.cursor.return_value

    tenant_id = onboard_new_tenant("Acme Corp", "acme", "pro")

    assert tenant_id is not None
    insert_sql = mock_cur.execute.call_args_list[0][0][0]
    assert "INSERT INTO tenants" in insert_sql
    schema_arg = mock_cur.execute.call_args_list[0][0][1][4]
    assert schema_arg.startswith("tenant_")
    assert len(schema_arg) == len("tenant_") + 8


def test_schema_name_pattern():
    schema = f"tenant_{uuid.uuid4().hex[:8]}"
    assert schema.startswith("tenant_")
    assert len(schema) == len("tenant_") + 8

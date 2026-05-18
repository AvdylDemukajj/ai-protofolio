from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from api_service.main import app
from core.tenant_resolver import TenantContext, get_tenant_context

SAMPLE_TENANT = {
    "id": "00000000-0000-0000-0000-000000000001",
    "schema": "tenant_deadbeef",
    "plan": "free",
    "active": True,
    "subdomain": "acme",
}


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_data_mocked(client):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [(1, {"k": "v"})]

    class Ctx:
        tenant = SAMPLE_TENANT
        cursor = mock_cursor
        conn = MagicMock()

        def commit(self):
            pass

    def override():
        yield Ctx()

    app.dependency_overrides[get_tenant_context] = override
    try:
        response = client.get(
            "/api/v1/data",
            headers={"Host": "acme.localhost", "X-Tenant-Subdomain": "acme"},
        )
        assert response.status_code == 200
        assert response.json()[0]["content"] == {"k": "v"}
    finally:
        app.dependency_overrides.clear()


def test_unknown_tenant_returns_403(client):
    from unittest.mock import patch

    with patch("core.tenant_resolver.get_tenant_config", return_value=None):
        response = client.get("/api/v1/data", headers={"Host": "unknown.localhost"})
    assert response.status_code == 403

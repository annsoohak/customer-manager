"""Feature router registration tests."""

from fastapi.testclient import TestClient
import pytest

from app.main import app


@pytest.mark.parametrize(
    ("path", "module"),
    [
        ("/api/auth/status", "auth"),
        ("/api/customers", "customers"),
        ("/api/dashboard", "dashboard"),
    ],
)
def test_feature_router_is_registered(path: str, module: str) -> None:
    with TestClient(app) as client:
        response = client.get(path)

    assert response.status_code == 200
    assert response.json() == {"module": module, "status": "ready"}

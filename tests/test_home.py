"""Home endpoint smoke test."""

from fastapi.testclient import TestClient

from app.main import app


def test_home_returns_200_ok() -> None:
    """홈 화면이 정상적으로 응답하는지 확인한다."""

    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

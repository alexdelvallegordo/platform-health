from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_liveness():

    response = client.get(
        "/health/live"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "alive",
        "service": "Platform Health",
        "version": "1.0.0",
    }


def test_readiness():

    response = client.get(
        "/health/ready"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "ready",
        "service": "Platform Health",
        "version": "1.0.0",
    }

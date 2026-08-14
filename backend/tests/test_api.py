from fastapi.testclient import TestClient

from app.main import app
from app.services.risk_service import calculate_risk


client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_safe_change_plan() -> None:
    response = client.post(
        "/api/changes",
        json={"request": "Increase the payment API timeout from 2 seconds to 5 seconds."},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "planned"
    assert body["plan"]["changes"][0]["new_code"] == "PAYMENT_TIMEOUT = 5"


def test_create_dangerous_change_plan() -> None:
    response = client.post(
        "/api/changes",
        json={"request": "Increase the payment API timeout from 2 seconds to 60 seconds."},
    )
    assert response.status_code == 201
    assert response.json()["plan"]["risk_level"] == "high"


def test_safe_risk_is_18() -> None:
    risk = calculate_risk(
        tests_failed=0,
        files_changed=["config.py"],
        requested_timeout=5,
    )
    assert risk == {
        "score": 18,
        "level": "low",
        "reasons": [
            "Change scope is limited and explicit",
            "Runtime configuration is modified",
            "All sandbox tests passed",
        ],
        "recommendation": "approve",
    }


def test_dangerous_risk_is_87() -> None:
    risk = calculate_risk(
        tests_failed=1,
        files_changed=["config.py"],
        requested_timeout=60,
    )
    assert risk["score"] == 87
    assert risk["level"] == "high"
    assert risk["recommendation"] == "reject"


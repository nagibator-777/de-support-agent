from fastapi.testclient import TestClient

from app.main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_incident():
    payload = {
        "title": "HDFS недоступен для записи",
        "log": "NameNode is in safe mode. Resources are low.",
        "use_llm": False,
    }

    with TestClient(app) as client:
        response = client.post("/api/v1/incidents/analyze", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "hadoop"
    assert body["severity"] == "high"
    assert body["llm_used"] is False

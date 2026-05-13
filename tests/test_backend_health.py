"""FastAPI 后端契约测试（不启动真实浏览器）。"""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_scraper_status_shape():
    r = client.get("/api/scraper/status")
    assert r.status_code == 200
    data = r.json()
    assert "is_running" in data
    assert data["is_running"] is False


def test_openapi_json():
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    assert spec.get("openapi", "").startswith("3.")
    assert "paths" in spec

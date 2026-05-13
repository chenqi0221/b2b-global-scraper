"""Google OAuth 路由契约（不触发浏览器）。"""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_google_oauth_status_shape():
    r = client.get("/api/google/oauth/status")
    assert r.status_code == 200
    data = r.json()
    assert "project_root" in data
    assert "client_secret_present" in data
    assert "token_present" in data

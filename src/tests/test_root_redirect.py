from conftest import client


def test_root_redirect_browser():
    """Browser user-agent should redirect to /docs"""
    response = client.get("/", headers={"User-Agent": "Mozilla/5.0 Chrome"})
    assert response.status_code == 200  # RedirectResponse with 200 in TestClient
    assert "/docs" in str(response.url) or response.history


def test_root_api_info():
    """Programmatic access should return API info JSON"""
    response = client.get("/", headers={"User-Agent": "curl/7.68.0"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert data["version"] == "3.0"